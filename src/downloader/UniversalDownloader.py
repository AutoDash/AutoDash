#!/usr/bin/env python3
import re
import os
from src.downloader.iDownloader import iDownloader
from src.data.VideoItem import VideoItem
from src.data.MetaDataItem import MetaDataItem
from src.executor.iExecutor import iExecutor

class UniversalDownloader(iExecutor):
    def __init__(self, *args):
        super().__init__(*args);
        self.registered_downloaders = []
        self.pathname = os.getcwd()
        
    def register_downloader(self, regex: str, downloader: iDownloader):
        self.registered_downloaders.append((regex, downloader))
        downloader.set_pathname(self.pathname)
        return self

    def run(self, metadata_item: MetaDataItem) -> VideoItem:
        for regex, downloader in self.registered_downloaders:
            if re.search(regex, metadata_item.url): return downloader.run(metadata_item)
        else:
            raise RuntimeError(f"No registered downloader can handle link: {metadata_item.url}")

    def set_pathname(self, pathname):
        self.pathname = pathname
        for _, downloader in self.registered_downloaders:
            downloader.set_pathname(pathname)
        return self
               
