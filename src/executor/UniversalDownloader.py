#!/usr/bin/env python3
import re
import os

from ..VideoStorageService import VideoStorageService
from ..downloader.iDownloader import iDownloader
from ..data.VideoItem import VideoItem
from ..data.MetaDataItem import MetaDataItem
from .iExecutor import iExecutor
from ..downloader.YoutubeDownloader import YoutubeDownloader
from ..downloader.ImgurDownloader import ImgurDownloader

class UniversalDownloader(iExecutor):
    def __init__(self, *args):
        super().__init__(*args)
        self.registered_downloaders = []

        self.video_storage = VideoStorageService()

        self.register_downloader("(.*youtube.*|.*youtu\.be.*)", YoutubeDownloader())
        self.register_downloader(".*imgur.*", ImgurDownloader())

    def register_downloader(self, regex: str, downloader: iDownloader):
        self.registered_downloaders.append((regex, downloader))
        downloader.set_video_storage(self.video_storage)
        return self

    def run(self, metadata_item: MetaDataItem) -> VideoItem:
        if self.video_storage.video_exists(metadata_item):
            return self.video_storage.load_video(metadata_item)

        for regex, downloader in self.registered_downloaders:
            if re.search(regex, metadata_item.url): return downloader.run(metadata_item)
        else:
            raise RuntimeError(f"No registered downloader can handle link: {metadata_item.url}")

    def set_pathname(self, pathname):
        self.video_storage.update_storage_dir(pathname)
        return self
