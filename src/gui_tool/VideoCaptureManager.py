import numpy as np
from .VideoFileManager import VideoFileManager

class VideoCaptureManager(object):
    def __init__(self, file_loc: str):
        self.file_loc = file_loc
        self.vfm = VideoFileManager(file_loc)
        self.paused = False

    def start_from(self, location: int = 0):
        self.vfm.start_from(location)

    def shift_frame_index(self, shift: int):
        self.vfm.start_from(
            max(
                min(
                    self.get_frame_index() + shift,
                    self.get_frames_count()-1
                ),
                0
            )
        )

    def release(self):
        self.vfm.release()
    def next(self) -> np.ndarray:
        if not self.paused:
            frame = self.vfm.next()
        else:
            frame = self.vfm.current()
        return frame
    def get_frames_count(self) -> int:
        return self.vfm.get_frames_count()
    def get_frame_index(self) -> int:
        return self.vfm.get_frame_index()
    def get_paused(self) -> bool:
        return self.paused
    def set_paused(self, paused: bool):
        self.paused = paused
    def is_open(self) -> bool:
        return self.vfm.is_open() and self.get_paused()
    def get_height(self):
        return self.vfm.get_height()
    def get_width(self):
        return self.vfm.get_width()