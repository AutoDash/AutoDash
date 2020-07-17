from abc import ABC, abstractmethod
from data.VideoItem import VideoItem
from executor.iExecutor import iExecutor
from data.MetaDataItem import MetaDataItem
import asyncio
import os

class DownloadException(RuntimeError):
    '''Raise on download failure'''

class iDownloader(iExecutor):
    def __init__(self, *args, pathname:str = os.getcwd(), **kwargs):
        super().__init__(*args, **kwargs)
        self.pathname = pathname

    @abstractmethod
    async def download(self, md_item: MetaDataItem) -> VideoItem:
        pass

    def run(self, md_item: MetaDataItem):
        return asyncio.run(self.download(md_item))

    def set_pathname(self, pathname):
        self.pathname = pathname
        return self
