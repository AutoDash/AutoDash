from .MetaDataItem import MetaDataItem
import hashlib
import numpy as np
import skvideo.io

class VideoItem:
    def __init__(self, filepath=None, metadata=None):
        self.filepath=filepath
        self.metadata=metadata
        # TODO: use cv2 to read mp4
        if self.filepath:
            self.npy = skvideo.io.vread(self.filepath)
        elif self.metadata:
            self.npy = skvideo.io.vread(self.metadata.location)
        else:
            raise ValueError("Missing filepath and metadata item") 


    def encode(self):
        if metadata is None:
            print("No metadata loaded")
            return None
        return self.metadata.encode()

    def update_storage_location(self, id: str):
        pass

    def save_and_close(self, **kwargs):
        file_path = kwargs.get('file_path', self.file_path)
        

