from .context import GUIContext
from typing import List

class SPContext(GUIContext):
    def __init__(self, file_loc: str, start_index=None, end_index=None):
        super(SPContext, self).__init__(file_loc, start_index, end_index)
        self.initial_enum_tags = []

    def set_bbox_fields_from_list(self, fields: List):
        self.bbox_fields = fields

    def get_bbox_fields(self):
        return self.bbox_fields

    def get_bbox_fields_as_list(self):
        return self.bbox_fields

    def set_additional_tags(self, tags):
        self.additional_tags = tags
