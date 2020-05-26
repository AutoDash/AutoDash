from .MetaDataItem import MetaDataItem
import hashlib
import numpy as np

class VideoItem:
    def __init__(self, file_path):
        self.file_path = file_path
        self.image = np.load(file_path)

    def update_storage_location(self, id: str):
        pass

    def save_and_close(self, **kwargs):
        file_path = kwargs.get('file_path', self.file_path)
        

