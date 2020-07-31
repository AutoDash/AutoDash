
from .VideoCaptureManager import VideoCaptureManager
from .VideoTaggingResults import VideoTaggingResults

class VideoTaggingContext(object):
    def __init__(self, file_loc: str, bbox_fields):
        self.file_loc = file_loc
        self.vcm = VideoCaptureManager(file_loc)
        self.vcm.start_from(0)
        self.result = VideoTaggingResults()
        self.file_height = self.vcm.get_height()
        self.file_width = self.vcm.get_width()

        self.bbox_fields = bbox_fields