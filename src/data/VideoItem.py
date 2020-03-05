import MetaDataItem

class VideoItem:
    def __init__(self, file_name:str, video_data:bytes, meta_data:MetaDataItem):
        self.file_name = file_name
        self.video_data = video_data
        self.meta_data = meta_data

    def update_storage_location(self, id: str):
        pass

