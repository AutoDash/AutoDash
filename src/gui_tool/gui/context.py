
from ..VideoCaptureManager import VideoCaptureManager

class GUIContext(object):
    def __init__(self, file_loc: str, start_index=None, end_index=None, enum_tags=None, to_be_deleted=False):
        self.file_loc = file_loc
        self.start_index = start_index
        self.end_index = end_index
        self.enum_tags = enum_tags if enum_tags is not None else enum_tags
        self.vcm = VideoCaptureManager(file_loc, start_index, end_index)
        self.vcm.start_from(0)
        self.file_height = self.vcm.get_height()
        self.file_width = self.vcm.get_width()

        self.is_dashcam = True
        self.to_be_deleted = to_be_deleted

    def mark_is_dashcam(self, is_dashcam: bool):
        self.marked = True
        self.is_dashcam = is_dashcam

    def mark_to_be_deleted(self, to_be_deleted: bool):
        self.marked = True
        self.to_be_deleted = to_be_deleted
