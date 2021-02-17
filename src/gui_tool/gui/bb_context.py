from .context import GUIContext
from typing import List
from ...data.BBFields import BBFields


class BBContext(GUIContext):
    def __init__(self,
                 file_loc: str,
                 bbox_fields: BBFields,
                 start_index=None,
                 end_index=None,
                 enum_tags=None,
                 to_be_deleted=False):
        super(BBContext, self).__init__(file_loc, start_index, end_index,
                                        enum_tags, to_be_deleted)
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
