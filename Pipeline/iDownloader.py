from abc import ABC, abstractmethod
import VideoItem

class iDownloader(ABC):
    def __init__(self):
        super().__init__

    @abstractmethod
    async def download(self, link:str) -> VideoItem:
        pass
