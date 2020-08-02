
from .VideoCaptureManager import VideoCaptureManager

class VideoTaggingContext(object):
    def __init__(self, file_loc: str, bbox_fields):
        self.file_loc = file_loc
        self.vcm = VideoCaptureManager(file_loc)
        self.vcm.start_from(0)
        self.file_height = self.vcm.get_height()
        self.file_width = self.vcm.get_width()

        self.bbox_fields = None
        self.set_bbox_fields(bbox_fields)

        self.is_dashcam = True
        self.additional_tags = {}

    def set_bbox_fields(self, fields):
        fields = list(fields)
        for i in range(len(fields)):
            if fields[i] == None:
                fields[i] = []
        assert(len(set([len(f) for f in fields])) == 1)
        self.bbox_fields = fields

    def get_bbox_fields(self):
        return self.bbox_fields

    def mark_is_dashcam(self, is_dashcam: bool):
        self.marked = True
        self.is_dashcam = is_dashcam

    def set_additional_tags(self, tags):
        self.additional_tags = tags