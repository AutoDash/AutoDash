#!/usr/bin/env python3
import re
from src.downloader.iDownloader import iDownloader
from src.data.VideoItem import VideoItem

class UniversalDownloader(iDownloader):
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs);
        self.registered_downloaders = []
        
    def register_downloader(self, regex: str, downloader: iDownloader):
        self.registered_downloaders.append((regex, download))

    async def download(self, link:str) -> VideoItem:
        for regex, downloader in self.registered_downloaders:
            if re.search(regex, link): return downloader.download(link)
        else:
            raise RuntimeError(f"No registered downloader can handle link: {link}")
               
