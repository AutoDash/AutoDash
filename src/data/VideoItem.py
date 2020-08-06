from .MetaDataItem import MetaDataItem
import hashlib
import numpy as np
import skvideo.io

class VideoItem:
    def __init__(self, metadata, filepath=None):
        self.filepath = filepath
        self.metadata = metadata
        self.npy = None
        # TODO: use cv2 to read mp4
        if filepath:
            self.npy = skvideo.io.vread(self.filepath)


    def encode(self):
        if self.metadata is None:
            print("No metadata loaded")
            return None
        return self.metadata.encode()

    def update_storage_location(self, id: str):
        pass

    def save_and_close(self, **kwargs):
        file_path = kwargs.get('file_path', self.file_path)
        

