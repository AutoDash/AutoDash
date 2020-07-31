#!/usr/bin/env python3
from .iDownloader import iDownloader
from ..data.VideoItem import VideoItem
from ..data.MetaDataItem import MetaDataItem
from imgur_downloader import ImgurDownloader as imgur
import os

class ImgurDownloader(iDownloader):
    async def download(self, md_idem: MetaDataItem) -> VideoItem:
        link = md_item.url
        downloader = imgur(link, dir_download=self.pathname, file_name=link)
        downloader.on_image_download(self.on_download_callback)
        downloader.save_images()
        return VideoItem(filepath=os.path.join(self.pathname, self.file_name), metadata=md_item)

    def on_download_callback(self, pos, url, file):
        self.file_name = file
