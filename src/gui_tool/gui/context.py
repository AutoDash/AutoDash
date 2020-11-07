
from ..VideoCaptureManager import VideoCaptureManager

class GUIContext(object):
    def __init__(self, file_loc: str, start_index=None, end_index=None):
        self.file_loc = file_loc
        self.vcm = VideoCaptureManager(file_loc, start_index, end_index)
        self.vcm.start_from(0)
        self.file_height = self.vcm.get_height()
        self.file_width = self.vcm.get_width()

        self.is_dashcam = True
        self.enum_tags = []

    def mark_is_dashcam(self, is_dashcam: bool):
        self.marked = True
        self.is_dashcam = is_dashcam