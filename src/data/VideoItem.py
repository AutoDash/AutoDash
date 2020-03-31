from .MetaDataItem import MetaDataItem
import hashlib

class VideoItem:
    def __init__(self, width:bytes, height:bytes, time:bytes, rgb:bytes, meta_data:MetaDataItem):
        self.width = width
        self.height = height
        self.time = time
        self.rgb = rgb
        self.meta_data = meta_data

    def encode(self):
        return self.meta_data.encode()

    def update_storage_location(self, id: str):
        pass
