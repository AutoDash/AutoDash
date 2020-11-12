from .context import GUIContext
from typing import List

class BBContext(GUIContext):
    def __init__(self, file_loc: str, bbox_fields: List, start_index=None, end_index=None):
        super(BBContext, self).__init__(file_loc, start_index, end_index)
        self.bbox_fields = bbox_fields
        self.additional_tags = {}

    def set_bbox_fields_from_list(self, fields: List):
        self.bbox_fields = fields

    def get_bbox_fields(self):
        return self.bbox_fields

    def get_bbox_fields_as_list(self):
        return self.bbox_fields

    def set_additional_tags(self, tags):
        self.additional_tags = tags
