#!/usr/bin/env python3
import re
from src.downloader.iDownloader import iDownloader
from src.data.VideoItem import VideoItem
from src.data.MetaDataItem import MetaDataItem
from src.executor.iExecutor import iExecutor

class UniversalDownloader(iExecutor):
    def __init__(self, *args):
        super().__init__(*args);
        self.registered_downloaders = []
        
    def register_downloader(self, regex: str, downloader: iDownloader):
        self.registered_downloaders.append((regex, downloader))
        return self

    def run(self, md_item: MetaDataItem) -> VideoItem:
        for regex, downloader in self.registered_downloaders:
            if re.search(regex, md_item.url): return downloader.run(md_item)
        else:
            raise RuntimeError(f"No registered downloader can handle link: {link}")
               
