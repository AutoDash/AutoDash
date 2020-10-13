from .context import GUIContext

class BBContext(GUIContext):
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
    def __init__(self, file_loc: str, bbox_fields, start_index=None, end_index=None):
        super(BBContext, self).__init__(file_loc, start_index, end_index)
        self.bbox_fields = None
        self.set_bbox_fields(bbox_fields)

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

    def set_additional_tags(self, tags):
        self.additional_tags = tags