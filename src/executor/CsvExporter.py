from .iExecutor import iExecutor
from ..data.VideoItem import VideoItem
from ..data.VideoFile import VideoFile
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
        video = VideoFile(item.filepath)
        video.set_index(metadata.start_i)
        video_width = video.get_frame_width()
        video_height = video.get_frame_height()
        timeframes = video.get_timeframe_range(metadata.end_i)
        timeframes = np.array(timeframes)
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
        time_begin = timeframes[0]
        time_end = timeframes[-1]
        headers = [FRAME, ID, CLASS, X1, Y1, X2, Y2, HAS_COLLISION]

        dtype = [
            (FRAME, np.int),
            (ID, np.int),
            (CLASS, np.object),
            (X1, np.float),
            (Y1, np.float),
            (X2, np.float),
            (Y2, np.float),
            (HAS_COLLISION, np.int),
        ]

        data = np.array(bbs, dtype=dtype)

        #data = np.array([*zip(frames, bbs[ID], bbs[CLASS], 
        #    bbs[X1], bbs[Y1], bbs[X2], bbs[Y2], bbs[HAS_COLLISION])])

        # Sort data by object id
        data = np.sort(data, order=ID)

        # Group data by object id
        _, unique_indices = np.unique(data[ID], return_index=True)
        data = np.split(data, unique_indices[1:], axis=0)

        interp_data = []
        n_frames = int((time_end - time_begin) * self.target_fps / 1000) 
        interp_time = time_begin + np.arange(n_frames) * (time_end - time_begin) / (n_frames - 1)
        for unique_object in data:
            if unique_object.shape[0] == 0:
                continue
            # Sort data by frame
            unique_object = np.sort(unique_object, order=FRAME)
            # Deal with holes
            interp_frame = np.arange(n_frames)
            holes, = np.where((unique_object[FRAME][1:] - unique_object[FRAME][:-1]) != 1)
            # Need +1 to have correct index for insertion
            holes = holes + 1
            label_id = unique_object[ID][0]
            label_class = unique_object[CLASS][0]
            label_collision = unique_object[HAS_COLLISION][0]
            nan_frame = (0, label_id, label_class, np.nan, np.nan, np.nan, np.nan, label_collision)
            time = timeframes[unique_object[FRAME]]
            unique_object = np.insert(unique_object, holes, nan_frame, axis=0)
            time = np.insert(time, holes, np.nan)
            interp_x1 = np.interp(interp_time, time, unique_object['x1s'], left=float('nan'), right=float('nan'))
            interp_x1 = interp_x1.clip(0, video_width - 1)
            interp_y1 = np.interp(interp_time, time, unique_object['y1s'], left=float('nan'), right=float('nan'))
            interp_y1 = interp_y1.clip(0, video_height - 1)
            interp_x2 = np.interp(interp_time, time, unique_object['x2s'], left=float('nan'), right=float('nan'))
            interp_x2 = interp_x2.clip(0, video_width - 1)
            interp_y2 = np.interp(interp_time, time, unique_object['y2s'], left=float('nan'), right=float('nan'))
            interp_y2 = interp_y2.clip(0, video_height - 1)
            interp_data += [ (frame, label_id, label_class, x1, y1, x2, y2, label_collision) 
                    for (frame, x1, y1, x2, y2) 
                    in zip(interp_frame, interp_x1, interp_y1,
                        interp_x2, interp_y2)
                    ]

        
        # Sort data by frame
        interp_data = np.array(interp_data, dtype=dtype)
        nan_mask = np.array([list(row) for row in interp_data[['x1s','x2s','y1s','y2s']]])
        nan_mask = np.any(np.isnan(nan_mask), axis=1)
        interp_data = interp_data[~nan_mask]
        interp_data = interp_data[np.argsort(interp_data['frames']), ...]
        interp_data['x1s'] = np.round(interp_data['x1s'])
        interp_data['y1s'] = np.round(interp_data['y1s'])
        interp_data['x2s'] = np.round(interp_data['x2s'])
        interp_data['y2s'] = np.round(interp_data['y2s'])

        directory = STORAGE_DIR_POSITIVES if len(collision_locations) else STORAGE_DIR_NEGATIVES
        filename = str(metadata.id) + ".csv"
        np.savetxt(directory / filename, interp_data, delimiter=',',
            fmt='%d,%d,%s,%d,%d,%d,%d,%d',
            comments='')
        stream = ffmpeg.input(item.filepath)
        stream = stream.trim(start_frame=begin, end_frame=end)
        stream = ffmpeg.filter(stream, 'fps', fps=self.target_fps, round='near')
        stream = ffmpeg.setpts(stream, expr='PTS-STARTPTS')
        stream = stream.output(str(STORAGE_DIR_VIDEOS / (str(metadata.id) + '.mp4')))
        stream = ffmpeg.overwrite_output(stream)
        try:
            stream.run()
        except KeyboardInterrupt:
            # Prevent corrupting video
            stream.run()
            raise
        print(f"Done exporting file {filename}")
        return item

