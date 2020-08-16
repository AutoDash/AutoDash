
from .VideoCaptureManager import VideoCaptureManager

class VideoTaggingContext(object):
    REQUIRED_BBOX_FIELDS =[
        "frames",
        "ids",
        "clss",
        "x1s",
        "y1s",
        "x2s",
        "y2s",
        "has_collision",
    ]
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

    def set_bbox_fields(self, fields: dict):
        if fields is None:
            fields = dict()
            for f in self.REQUIRED_BBOX_FIELDS:
                fields[f] = []

        assert(all([(x in fields) for x in self.REQUIRED_BBOX_FIELDS]))
        for key in fields.keys():
            if fields[key] is None:
                fields[key] = []
        assert(len(set([len(f) for f in fields.values()])) == 1)
        self.bbox_fields = fields

    def set_bbox_fields_from_list(self, args):
        assert(len(args) == len(self.REQUIRED_BBOX_FIELDS))
        self.set_bbox_fields(dict([
            (name, val) for name, val in zip(self.REQUIRED_BBOX_FIELDS, args)
        ]))

    def get_bbox_fields(self):
        return self.bbox_fields

    def get_bbox_fields_as_list(self):
        return [
            self.bbox_fields["frames"],
            self.bbox_fields["ids"],
            self.bbox_fields["clss"],
            self.bbox_fields["x1s"],
            self.bbox_fields["y1s"],
            self.bbox_fields["x2s"],
            self.bbox_fields["y2s"],
            self.bbox_fields["has_collision"]
        ]

    def mark_is_dashcam(self, is_dashcam: bool):
        self.marked = True
        self.is_dashcam = is_dashcam

    def set_additional_tags(self, tags):
        self.additional_tags = tags