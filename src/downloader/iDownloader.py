from abc import ABC, abstractmethod
import VideoItem
import os

class iDownloader(ABC):
    def __init__(self, pathname:str = os.getcwd()):
        super().__init__
        self.pathname = pathname

    @abstractmethod
    async def download(self, link:str) -> VideoItem:
        pass
