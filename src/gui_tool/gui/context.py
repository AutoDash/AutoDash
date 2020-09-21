
from ..VideoCaptureManager import VideoCaptureManager

class GUIContext(object):
    def __init__(self, file_loc: str):
        self.file_loc = file_loc
        self.vcm = VideoCaptureManager(file_loc)
        self.vcm.start_from(0)
        self.file_height = self.vcm.get_height()
        self.file_width = self.vcm.get_width()

        self.is_dashcam = True

    def mark_is_dashcam(self, is_dashcam: bool):
        self.marked = True
        self.is_dashcam = is_dashcam