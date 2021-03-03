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
            (X1, np.int),
            (Y1, np.int),
            (X2, np.int),
            (Y2, np.int),
            (HAS_COLLISION, np.int),
        ]

        bbs = np.array(bbs, dtype=dtype)
        frames = np.array(bbs[FRAME])

        data = np.array([*zip(frames, bbs[ID], bbs[CLASS], 
            bbs[X1], bbs[Y1], bbs[X2], bbs[Y2], bbs[HAS_COLLISION])], dtype=str)

        # Sort data by object id
        data = data[np.argsort(data[:,1].astype(int)), ...]

        # Group data by object id
        _, unique_indices = np.unique(data[:,1], return_index=True)
        data = np.split(data, unique_indices[1:], axis=0)

        interp_data = []
        n_frames = int((time_end - time_begin) * self.target_fps / 1000) 
        interp_time = time_begin + np.arange(n_frames) * (time_end - time_begin) / (n_frames - 1)
        for unique_object in data:
            if unique_object.shape[0] == 0:
                continue
            # Sort data by frame
            unique_object = unique_object[np.argsort(unique_object[:,0].astype(int)), ...]
            time = timeframes[unique_object[:,0].astype(int)]
            label_id = unique_object[0, 1]
            label_class = unique_object[0, 2]
            label_collision = unique_object[0, 7]
            # @TODO (vroch): Need to insert nan frames for each hole in frames to prevent interpolating over holes
            interp_frame = np.arange(n_frames)
            interp_x1 = np.interp(interp_time, time, unique_object[:,3].astype(np.float), left=float('nan'), right=float('nan'))
            interp_x1 = interp_x1.clip(0, video_width - 1)
            interp_y1 = np.interp(interp_time, time, unique_object[:,4].astype(np.float), left=float('nan'), right=float('nan'))
            interp_y1 = interp_y1.clip(0, video_height - 1)
            interp_x2 = np.interp(interp_time, time, unique_object[:,5].astype(np.float), left=float('nan'), right=float('nan'))
            interp_x2 = interp_x2.clip(0, video_width - 1)
            interp_y2 = np.interp(interp_time, time, unique_object[:,6].astype(np.float), left=float('nan'), right=float('nan'))
            interp_y2 = interp_y2.clip(0, video_height - 1)
            interp_data += [ (frame, label_id, label_class, x1, y1, x2, y2, label_collision) 
                    for (frame, x1, y1, x2, y2) 
                    in zip(interp_frame, interp_x1, interp_y1,
                        interp_x2, interp_y2)
                    ]

        
        # Sort data by frame
        interp_data = np.array(interp_data)
        nan_mask = np.any(np.isnan(interp_data[:,(0,3,4,5,6)].astype(np.float)), axis=1)
        interp_data = interp_data[~nan_mask]
        interp_data = interp_data[np.argsort(interp_data[:,0].astype(np.int)), ...]
        interp_data[:,3] = np.round(interp_data[:,3].astype(np.float)).astype(np.int)
        interp_data[:,4] = np.round(interp_data[:,4].astype(np.float)).astype(np.int)
        interp_data[:,5] = np.round(interp_data[:,5].astype(np.float)).astype(np.int)
        interp_data[:,6] = np.round(interp_data[:,6].astype(np.float)).astype(np.int)

        directory = STORAGE_DIR_POSITIVES if len(collision_locations) else STORAGE_DIR_NEGATIVES
        filename = str(metadata.id) + ".csv"
        np.savetxt(directory / filename, interp_data, delimiter=',',
            fmt='%s,%s,%s,%s,%s,%s,%s,%s',
            comments='')
        stream = ffmpeg.input(item.filepath)
        stream = stream.trim(start_frame=begin, end_frame=end, duration=5)
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

