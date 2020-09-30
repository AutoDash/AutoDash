import cv2
import numpy as np
import os.path
from .GUIExceptions import VideoNotFoundException, VideoCouldNotBeOpenedException

"""
A utility class for retrieving frames from local file
Note
    Opencv is 1 indexed.
    get_frame_index() = 0 indicates that the first frame has not yet been retrieved
"""
class VideoFileManager(object):
    def __init__(self, file_loc: str):
        self.file_loc = file_loc
        self.capture = None
        self.current_frame = None
        if not (os.path.isfile(file_loc)):
            raise VideoNotFoundException("Requested video file does not exist")

    def _set_capture(self, skip_n: int = 0):
        if self.capture is not None:
            self.capture.release()
        self.capture = cv2.VideoCapture(self.file_loc)

        if not (self.is_open()):
            raise VideoCouldNotBeOpenedException("Video format could not be read by opencv")

        if skip_n > 0:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, skip_n-1)
            ret, self.current_frame = self.capture.read()

    def start_from(self, location: int = 0):
        self._set_capture(location)

    def release(self):
        self.capture.release()

    def next(self) -> np.ndarray:
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                self.current_frame = frame
        return self.current_frame

    def current(self):
        return self.current_frame

    def get_frames_count(self) -> int:
        return int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_frame_index(self) -> int:
        return int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))

    def is_open(self) -> bool:
        return self.capture.isOpened() and self.get_frame_index() < self.get_frames_count()

    def get_width(self):
        return int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    def get_height(self):
        return int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def extract_remaining(self):
        frames = []
        while self.is_open():
            frame = self.next()
            frames.append(frame)
        return frames