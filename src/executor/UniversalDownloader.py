#!/usr/bin/env python3
import re
import os
import cv2

from ..VideoStorageService import VideoStorageService
from ..downloader.iDownloader import iDownloader
from ..data.VideoItem import VideoItem
from ..data.MetaDataItem import MetaDataItem
from .iExecutor import iExecutor
from ..downloader.YoutubeDownloader import YoutubeDownloader
# from ..downloader.ImgurDownloader import ImgurDownloader # temporarily removed because it cant be fetched with pip

class UniversalDownloader(iExecutor):
    def __init__(self, *args):
        super().__init__(*args)
        self.registered_downloaders = []

        self.video_storage = VideoStorageService()

        self.register_downloader("(.*youtube.*|.*youtu\.be.*)", YoutubeDownloader())
        # self.register_downloader(".*imgur.*", ImgurDownloader())

    def register_downloader(self, regex: str, downloader: iDownloader):
        self.registered_downloaders.append((regex, downloader))
        downloader.set_video_storage(self.video_storage)
        return self

    def run(self, metadata_item: MetaDataItem) -> VideoItem:
        vid_item = None
        if self.video_storage.video_exists(metadata_item):
            vid_item = VideoItem(metadata=metadata_item, filepath=self.video_storage.get_existing_file_with_ext(metadata_item))
        else:
            for regex, downloader in self.registered_downloaders:
                if re.search(regex, metadata_item.url):
                    vid_item = downloader.run(metadata_item)
                    break
            else:
                raise RuntimeError(f"No registered downloader can handle link: {metadata_item.url}")
        
        cap = cv2.VideoCapture(vid_item.filepath)
        w,h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        vid_item.metadata.bb_fields.set_resolution((w,h))
        return vid_item

    def set_pathname(self, pathname):
        self.video_storage.update_storage_dir(pathname)
        return self
