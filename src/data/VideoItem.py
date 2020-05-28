from .MetaDataItem import MetaDataItem
import hashlib
import numpy as np
import skvideo.io

class VideoItem:
    def __init__(self, filename=None, metadata=None):
        self.filename=filename
        self.metadata=metadata

    def encode(self):
        return self.metadata.encode()

    def update_storage_location(self, id: str):
        pass

    def save_and_close(self, **kwargs):
        file_path = kwargs.get('file_path', self.file_path)
        

