from abc import ABC, abstractmethod

from VideoStorageService import VideoStorageService
from ..data.VideoItem import VideoItem
from ..executor.iExecutor import iExecutor
from ..data.MetaDataItem import MetaDataItem
import asyncio
import os

class DownloadException(RuntimeError):
    '''Raise on download failure'''

class iDownloader(iExecutor):
    def __init__(self, parents=[], **kwargs):
        super().__init__(parents, **kwargs)
        self.video_storage = None

    @abstractmethod
    async def download(self, md_item: MetaDataItem) -> VideoItem:
        pass

    def run(self, md_item: MetaDataItem):
        return asyncio.run(self.download(md_item))

    def set_video_storage(self, video_storage: VideoStorageService):
        self.video_storage = video_storage
        return self
