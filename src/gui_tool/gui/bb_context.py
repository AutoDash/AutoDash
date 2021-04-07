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
                 location="",
                 to_be_deleted=False):
        super(BBContext, self).__init__(file_loc, start_index, end_index,
                                        enum_tags, to_be_deleted)
        self.bbox_fields = bbox_fields
        self.reckless_intervals = []
        self.additional_tags = {}
        self.location = location

    def get_bbox_fields(self):
        return self.bbox_fields

    def get_bbox_fields_as_list(self):
        return self.bbox_fields.get_bbs_as_arrs()

    def set_additional_tags(self, tags):
        self.additional_tags = tags
    
    def set_location(self, location):
        self.location = location
