from abc import ABC, abstractmethod
import cv2
import numpy as np
import os
class VideoStartOrEndOutOfBoundsException(RuntimeError):
    '''Invalid start or end location in VideoFile'''

class VideoNotFoundException(RuntimeError):
    '''Raise when local video file could not be found'''

class VideoCouldNotBeOpenedException(RuntimeError):
    '''Raise when the local video file could not be properly read or opened'''

"""
Behaviour notes:
0 indexed. len(x) gives 1 over the max possible frame index (kinda like how max index of an array of length 10 is 9)
When accessing data, please use accessors rather than getting the fields directly
Check VideoFile.is_open() before calling next.
    If reached the end of the file, the last frame will be repeatedly returned
If turning to numpy array, note the dimensions

Example:
while vf.is_open():
    cv2.imshow('windowName', vf.next())
"""
class VideoFile(object):
    def __init__(self, file_loc, start: int = None, end: int = None):
        self.file_loc = file_loc

        if not (os.path.isfile(file_loc)):
            raise VideoNotFoundException("Requested video file does not exist")

        self.source = cv2.VideoCapture(file_loc)
        self.true_length = int(self.source.get(cv2.CAP_PROP_FRAME_COUNT))
        start = start if start is not None else 0
        end = end if end is not None else self.true_length
        self._start = start
        self._end = end

        if type(start) != int or type(end) != int \
                or end > self.true_length \
                or start < 0 \
                or end <= start:
            raise VideoStartOrEndOutOfBoundsException("Invalid range {0}-{1} for file of length {2}".format(
                start, end, self.true_length
            ))

        # Get properties
        self.frame_count = end - start
        self.frame_width = int(self.source.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.source.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.capture = None
        self._index = None
        self.set_index(0)

    def __alter_index(self, index: int) -> int:
        if not (self._start <= self._start + index < self._end):
            raise VideoStartOrEndOutOfBoundsException("Invalid index {0} for VideoFile of length {1}".format(
                index, self.frame_count))
        index = self._start + index
        return index

    def __revert_index(self, index: int) -> int:
        return index - self._start

    def __set_capture(self, skip_n: int = 0):
        if self.capture is not None:
            self.capture.release()

        skip_n = int(skip_n)
        self.capture = cv2.VideoCapture(self.file_loc)

        if not (self.is_open()):
            raise VideoCouldNotBeOpenedException("Video format could not be read by opencv")

        if skip_n > 0:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, skip_n)
        ret, self.current_frame = self.capture.read()

    def set_index(self, location: int = None):
        self.__set_capture(self.__alter_index(location))

    def get_index(self) -> int:
        return self.__revert_index(int(self.capture.get(cv2.CAP_PROP_POS_FRAMES)) - 1)

    def clear(self):
        self.capture.release()

    def next(self) -> np.ndarray:
        if self.is_open():
            ret, frame = self.capture.read()
            if ret:
                self.current_frame = frame
        return self.current_frame

    def current(self):
        return self.current_frame

    def get_frame_count(self) -> int:
        return self.frame_count

    def __len__(self):
        return self.get_frame_count()

    def is_open(self) -> bool:
        return self.capture.isOpened() and self.get_index() < self.frame_count

    # Returns array with dimensions (frame_num, height, width, rgb)
    def as_numpy(self, start=None, end=None):
        start = start if start is not None else 0
        end = end if end is not None else self.get_frame_count()

        vf = VideoFile(self.file_loc, self._start, self._end)
        vf.set_index(start)
        ret = []
        while vf.is_open() and vf.get_index() < end:
            ret.append(vf.next())
        return np.array(ret)

    def get_width(self):
        return self.frame_width

    def get_height(self):
        return self.frame_height

    def release(self):
        self.capture.release()