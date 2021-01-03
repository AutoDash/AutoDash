from .MetaDataItem import MetaDataItem
import hashlib
import numpy as np
import skvideo.io
import ffmpeg

class VideoItem:
    def __init__(self, metadata, filepath=None):
        self.filepath = filepath
        self.metadata = metadata
        
        info = ffmpeg.probe(filepath)
        streams = [ stream for stream in info.get('streams', []) if stream.get('codec_type') == 'video']
        if len(streams) > 1:
            raise StopSignal(f"Video {item.id} has multiple video streams. Could not determine FPS")
        if len(streams) < 1:
            raise StopSignal(f"Video {item.id} has no video streams. Could not determine FPS")
        self.fps = float(streams[0]['nb_frames']) / float(streams[0]['duration'])

    def encode(self):
        if self.metadata is None:
            print("No metadata loaded")
            return None
        return self.metadata.encode()

    def update_storage_location(self, id: str):
        pass

    def save_and_close(self, **kwargs):
        file_path = kwargs.get('file_path', self.file_path)

    def to_json(self):
        return {
            "filepath": self.filepath,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return str(self.to_json())
