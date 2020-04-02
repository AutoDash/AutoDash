from abc import ABC, abstractmethod
from typing import List

from src.data.MetaDataItem import MetaDataItem

class iDatabase(ABC):
    def __init__(self):
        super().__init__

    @abstractmethod
    async def publish_new_metadata(self, metadata: MetaDataItem) -> str:
        pass

    # Returns 1 on Success and 0 on Failure
    @abstractmethod
    async def update_metadata(self, metadata: MetaDataItem) -> int:
        pass

    @abstractmethod
    async def fetch_metadata(self, id: str) -> MetaDataItem:
        pass

    @abstractmethod
    async def fetch_video_id_list(self) -> List[str]:
        pass

    @abstractmethod
    async def fetch_video_url_list(self) -> List[str]:
        pass
