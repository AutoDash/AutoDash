import MetaDataItem

class VideoItem:
    def __init__(self, video_data_width:bytes, video_data_height:bytes, video_data_time:bytes, video_data_rgb:bytes, meta_data:MetaDataItem):
        self.video_data_width = video_data_width
        self.video_data_height = video_data_height
        self.video_data_time = video_data_time
        self.video_data_rgb = video_data_rgb
        self.meta_data = meta_data

    def update_storage_location(self, id: str):
        pass

