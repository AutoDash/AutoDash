#!/usr/bin/env python3
from src.data.MetaDataItem import MetaDataItem
from src.data.VideoItem import VideoItem
import os, pickle
import glob

class VideoStorageService:
    def __init__(self, storage_dir=None):
        if storage_dir is None:
            self.storage_dir = os.path.join(os.getcwd(), "storage")
        else:
            self.storage_dir = storage_dir

        if not os.path.exists(self.storage_dir):
            os.mkdir(self.storage_dir)

    def update_storage_dir(self, new_storage_dir):
        old_dir = self.storage_dir
        if not os.path.exists(new_storage_dir):
            os.mkdir(self.storage_dir)

        self.storage_dir = new_storage_dir

        for file in os.listdir(old_dir):
            self.move_video(old_dir, file)


    def get_storage_dir(self):
        return self.storage_dir

    def __repr__(self):
        return f"VideoStorageService({self.storage_dir})"

    def store_video(self, item: VideoItem) -> None:
        with open(self.get_file(item), 'wb') as output:
            pickle.dump(item, output, pickle.HIGHEST_PROTOCOL)

    def move_video(self, cur_loc, new_name):
        new_path = os.path.join(self.storage_dir, new_name)
        os.rename(cur_loc, new_path)

    def video_exists(self, item: MetaDataItem) -> bool:
        return glob.glob(self.get_file(item)+ ".*")

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

    @staticmethod
    def get_file_name(item):
        return item.encode()

    def get_file(self, item) -> str:
        return os.path.join(self.storage_dir, self.get_file_name(item))
        
    def get_existing_file_with_ext(self, item) -> str:
        existing_files = glob.glob(self.get_file(item)+ ".*")
        if existing_files:
            return existing_files[0]
        return None
