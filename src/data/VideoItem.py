from .MetaDataItem import MetaDataItem
import hashlib
class VideoItem:
    def __init__(self, file_name:str, meta_data: MetaDataItem):
        self.file_name = file_name
        self.meta_data = meta_data

    def encode(self):
        return self.meta_data.encode()

    def update_storage_location(self, id: str):
        pass
