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

STORAGE_DIR_POSITIVES = Path(os.path.join(get_project_root(), "data_files_positives"))
STORAGE_DIR_POSITIVES.mkdir(parents=True, exist_ok=True)
STORAGE_DIR_NEGATIVES = Path(os.path.join(get_project_root(), "data_files_negatives"))
STORAGE_DIR_NEGATIVES.mkdir(parents=True, exist_ok=True)
STORAGE_DIR_VIDEOS = Path(os.path.join(get_project_root(), "feature_videos"))
STORAGE_DIR_VIDEOS.mkdir(parents=True, exist_ok=True)

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
        dtype = [
            ('frames', np.uint),
            ('ids', np.uint),
            ('clss', np.object),
            ('x1s', np.uint),
            ('y1s', np.uint),
            ('x2s', np.uint),
            ('y2s', np.uint),
            ('has_collision', np.uint),
        ]
        normalized_frames = np.array(bbs['frames'], dtype=np.int)
        begin = int(collision_frame - np.floor(self.clip_len_s * fps))
        if begin + self.len_thresh_s * fps < 0:
            # We are under the minimum threshold
            raise StopSignal(f"Video {item.id} is shorter than {self.len_thresh_s}s")
        begin = max(begin, 0)
        normalized_frames -= begin
        data = np.array([*zip(normalized_frames, bbs['ids'], bbs['clss'], 
            bbs['x1s'], bbs['y1s'], bbs['x2s'], bbs['y2s'], bbs['has_collision'])])
        data = data[np.logical_and(normalized_frames >= 0, normalized_frames <= collision_frame - begin)]
        data.sort(axis=0)
        data = np.split(data[:,1:], np.unique(data[:, 0], return_index=True)[1][1:])
        mask = np.floor(np.arange((collision_frame - begin) * self.target_fps / fps)).astype(int)
        
        # This line is broken
        data = data[mask].astype(dtype).flatten()

        directory = STORAGE_DIR_POSITIVES if np.any(data['has_collision']) else STORAGE_DIR_NEGATIVES
        filename = str(metadata.id) + ".csv"
        np.savetxt(directory / filename, data, delimiter=',',
            fmt='%d,%d,%s,%d,%d,%d,%d,%d',
            comments='')
        stream = ffmpeg.input(item.filepath)
        stream = stream.trim(start_frame=begin + metadata.start_i, end_frame=collision_frame + metadata.start_i)
        stream = ffmpeg.filter(stream, 'fps', fps=self.target_fps, round='up')
        stream = stream.output(str(STORAGE_DIR_VIDEOS / (str(metadata.id) + '.mp4')))
        stream = ffmpeg.overwrite_output(stream)
        stream.run()
        print(f"Done exporting file {filename}")
        return item

