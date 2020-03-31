#!/usr/bin/env python3
from src.data.MetaDataItem import MetaDataItem
from src.data.VideoItem import VideoItem
import os, pickle


class StorageService():
    def __init__(self):
        self.storage_dir = os.path.join(os.getcwd(), "storage")
        if not os.path.exists(self.storage_dir):
            os.mkdir(self.storage_dir)

    def __repr__(self):
        return f"StorageService({self.storage_dir})"

    def store_video(self, item: VideoItem) -> None:
        with open(self.get_file(item), 'wb') as output:
            pickle.dump(item, output, pickle.HIGHEST_PROTOCOL)

    def video_exists(self, item: MetaDataItem) -> bool:
        return os.path.exists(self.get_file(item))

    def load_video(self, item: MetaDataItem) -> VideoItem:
        return self.load_file(self.get_file(item))

    def load_file(self, filename: str) -> VideoItem:
        with open(filename, "rb") as input:
            return pickle.load(input)

    def list_videos(self) -> VideoItem:
        for filename in os.listdir(self.storage_dir):
            yield self.load_file(os.path.join(self.storage_dir, filename))

    def delete_video(self, item: MetaDataItem) -> None:
        file = self.get_file(item)
        if os.path.exists(file):
            os.remove(file)

    def delete_all(self) -> None:
        for video in self.list_videos():
            self.delete_video(video)

    def get_file(self, item) -> str:
        return os.path.join(self.storage_dir, item.encode())
