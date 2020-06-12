from abc import ABC, abstractmethod
from src.data.VideoItem import VideoItem
import os

class DownloadException(Exception):
    '''Raise on download failure'''

class iDownloader(ABC):
    def __init__(self, pathname:str = os.getcwd()):
        super().__init__()
        self.pathname = pathname

    @abstractmethod
    async def download(self, link:str) -> VideoItem:
        pass
