from .iExecutor import iExecutor
from ..data.VideoItem import VideoItem
from ..signals.StopSignal import StopSignal
from ..utils import get_project_root 
import os
import csv
import re
import numpy as np
from pathlib import Path
import ffmpeg
import pdb;

STORAGE_DIR_POSITIVES = Path(os.path.join(get_project_root(), "data_files_positives"))
STORAGE_DIR_POSITIVES.mkdir(parents=True, exist_ok=True)
STORAGE_DIR_NEGATIVES = Path(os.path.join(get_project_root(), "data_files_negatives"))
STORAGE_DIR_NEGATIVES.mkdir(parents=True, exist_ok=True)
STORAGE_DIR_VIDEOS = Path(os.path.join(get_project_root(), "feature_videos"))
STORAGE_DIR_VIDEOS.mkdir(parents=True, exist_ok=True)

FRAME, ID, CLASS, X1, Y1, X2, Y2, HAS_COLLISION = 'frames', 'ids', 'clss', 'x1s', 'y1s', 'x2s', 'y2s', 'has_collision'

class CsvExporter(iExecutor):
    def __init__(self, *parents, target_fps=20, clip_length='5s', length_threshold='3s'):
        super().__init__(*parents)
        self.target_fps = target_fps
        self.clip_len_s = CsvExporter.parse_time(clip_length)
        self.len_thresh_s = CsvExporter.parse_time(length_threshold)

    def parse_time(time):
        pattern = r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
        result = re.match(pattern, time)
        if not result:
            raise ValueError(f'Invalid time: {time}. Expected digit followed by [smh]')
        hours, minutes, seconds = result.groups()
        time_s = int(hours or 0)
        time_s *= 60
        time_s += int(minutes or 0)
        time_s *= 60
        time_s += int(seconds or 0)
        if time_s <= 0:
            raise ValueError(f'Invalid time: {time}. Expected a non-zero positive value')
        return time_s

    def run(self, item: VideoItem):
        print("Start exporting file")
        metadata = iExecutor.get_metadata(item)
        bbs = metadata.bb_fields.to_json()
        if bbs is None or len(bbs) == 0:
            raise StopSignal("No bounding box fields for this item")

        # First, we trim the last seconds before the first collision
        if not metadata.accident_locations or len(metadata.accident_locations) == 0:
            # TODO: This should be a negative
            raise StopSignal(f"No accident locations labelled for {item.id}")
        if not metadata.start_i:
            raise StopSignal(f"Metadata is not clipped")
        collision_frame = np.min(metadata.accident_locations)
        info = ffmpeg.probe(item.filepath)
        streams = [ stream for stream in info.get('streams', []) if stream.get('codec_type') == 'video']
        if len(streams) > 1:
            raise StopSignal(f"Video {item.id} has multiple video streams. Could not determine FPS")
        if len(streams) < 1:
            raise StopSignal(f"Video {item.id} has no video streams. Could not determine FPS")
        fps = float(streams[0]['nb_frames']) / float(streams[0]['duration'])

        headers = [FRAME, ID, CLASS, X1, Y1, X2, Y2, HAS_COLLISION]

        #dtype = [
        #    (FRAME, np.uint),
        #    (ID, np.uint),
        #    (CLASS, np.object),
        #    (X1, np.uint),
        #    (Y1, np.uint),
        #    (X2, np.uint),
        #    (Y2, np.uint),
        #    (HAS_COLLISION, np.uint),
        #]

        begin = int(collision_frame - np.floor(self.clip_len_s * fps))
        if begin + self.len_thresh_s * fps < 0:
            # We are under the minimum threshold
            raise StopSignal(f"Video {item.id} is shorter than {self.len_thresh_s}s")
        begin = max(begin, 0)

        normalized_frames = np.array(bbs[FRAME]).astype(np.int) - begin

        data = np.array([*zip(normalized_frames, bbs[ID], bbs[CLASS], 
            bbs[X1], bbs[Y1], bbs[X2], bbs[Y2], bbs[HAS_COLLISION])], dtype=str)
        
        data = data[np.logical_and(normalized_frames >= 0, normalized_frames <= collision_frame - begin), ...]

        # Sort data by frame
        data = data[np.argsort(data[:,0].astype(int)), ...]

        # Group data by frame
        _, unique_indices = np.unique(data[:,0].astype(np.int), return_index=True)
        data = np.array(np.split(data, unique_indices[1:], axis=0))
        
        # Mask for downsampling fps
        n_input_frames  = collision_frame - begin
        n_output_frames = round(n_input_frames * (self.target_fps / fps))
        sample_interval = float(n_input_frames) / n_output_frames

        # select frames to sample
        mask = np.round(np.arange(n_output_frames) * sample_interval).astype(int)
        mask = np.minimum(mask, data.shape[0] - 1)

        # Duplicate frames 
        # n_duplicate = n_input_frames - n_output_frames
        # dup_mask = mask[::n_output_frames // n_duplicate][:n_duplicate]
        # mask = np.sort(np.concatenate((mask, dup_mask)))

        data = data[mask]

        flatten = lambda x: [z for y in x for z in y]
        data = flatten(data)

        directory = STORAGE_DIR_POSITIVES if np.any(bbs[HAS_COLLISION]) else STORAGE_DIR_NEGATIVES
        filename = str(metadata.id) + ".csv"
        np.savetxt(directory / filename, data, delimiter=',',
            fmt='%s,%s,%s,%s,%s,%s,%s,%s',
            comments='')
        stream = ffmpeg.input(item.filepath)
        stream = stream.trim(start_frame=begin + metadata.start_i, end_frame=collision_frame + metadata.start_i)
        stream = ffmpeg.filter(stream, 'fps', fps=self.target_fps, round='near')
        stream = stream.output(str(STORAGE_DIR_VIDEOS / (str(metadata.id) + '.mp4')))
        stream = ffmpeg.overwrite_output(stream)
        stream.run()
        print(f"Done exporting file {filename}")
        return item

