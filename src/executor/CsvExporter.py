from .iExecutor import iExecutor
from ..data.VideoItem import VideoItem
from ..signals.SkipSignal import SkipSignal
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

FRAME, ID, CLASS, X1, Y1, X2, Y2, HAS_COLLISION = 'frames', 'ids', 'clss', 'x1s', 'y1s', 'x2s', 'y2s', 'has_collision'

class CsvExporter(iExecutor):
    def __init__(self, *parents, target_fps=20):
        super().__init__(*parents)
        self.target_fps = target_fps

    def run(self, item: VideoItem):
        print("Start exporting file")
        metadata = iExecutor.get_metadata(item)
        fps = item.fps
        bbs = metadata.bb_fields.get_bbs_as_arrs()
        if bbs is None or len(bbs) == 0:
            raise SkipSignal("No bounding box fields for this item")
        collision_locations = metadata.bb_fields.collision_locations

        if not metadata.start_i:
            raise SkipSignal(f"Metadata is not clipped")
        if not metadata.end_i:
            raise SkipSignal(f"Metadata is not clipped")
        begin = metadata.start_i
        end = metadata.end_i
        
        headers = [FRAME, ID, CLASS, X1, Y1, X2, Y2, HAS_COLLISION]

        dtype = [
            (FRAME, np.uint),
            (ID, np.uint),
            (CLASS, np.object),
            (X1, np.uint),
            (Y1, np.uint),
            (X2, np.uint),
            (Y2, np.uint),
            (HAS_COLLISION, np.uint),
        ]

        bbs = np.array(bbs, dtype=dtype)
        frames = np.array(bbs[FRAME])

        data = np.array([*zip(frames, bbs[ID], bbs[CLASS], 
            bbs[X1], bbs[Y1], bbs[X2], bbs[Y2], bbs[HAS_COLLISION])], dtype=str)

        # Sort data by frame
        data = data[np.argsort(data[:,0].astype(int)), ...]

        # Group data by frame
        _, unique_indices = np.unique(data[:,0].astype(np.int), return_index=True)
        data = np.array(np.split(data, unique_indices[1:], axis=0))
        
        # Mask for downsampling fps
        n_input_frames  = end - begin
        n_output_frames = round(n_input_frames * (self.target_fps / fps))
        sample_interval = float(n_input_frames) / n_output_frames

        # select frames to sample
        mask = np.round(np.arange(n_output_frames) * sample_interval).astype(int)
        mask = np.minimum(mask, data.shape[0] - 1)

        data = data[mask]

        flatten = lambda x: [z for y in x for z in y]
        data = flatten(data)

        directory = STORAGE_DIR_POSITIVES if len(collision_locations) else STORAGE_DIR_NEGATIVES
        filename = str(metadata.id) + ".csv"
        np.savetxt(directory / filename, data, delimiter=',',
            fmt='%s,%s,%s,%s,%s,%s,%s,%s',
            comments='')
        stream = ffmpeg.input(item.filepath)
        stream = stream.trim(start_frame=begin, end_frame=end, duration=5)
        stream = ffmpeg.filter(stream, 'fps', fps=self.target_fps, round='near')
        stream = ffmpeg.setpts(stream, expr='PTS-STARTPTS')
        stream = stream.output(str(STORAGE_DIR_VIDEOS / (str(metadata.id) + '.mp4')))
        stream = ffmpeg.overwrite_output(stream)
        stream.run()
        print(f"Done exporting file {filename}")
        return item

