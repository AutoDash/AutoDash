from abc import ABC, abstractmethod
from typing import List

from src.data.FilterCondition import FilterCondition
from src.data.MetaDataItem import MetaDataItem

class AlreadyExistsException(Exception):
    '''Raise on adding a video that is already stored'''

class NotExistingException(Exception):
    '''Raise on adding a video that does not exist in the database'''

class iDatabase(ABC):
    def __init__(self):
        super().__init__

    # Sets the id of the metadata to a unique identifier
    @abstractmethod
    async def publish_new_metadata(self, metadata: MetaDataItem) -> str:
        pass

    @abstractmethod
    async def update_metadata(self, metadata: MetaDataItem):
        pass

    @abstractmethod
    async def fetch_metadata(self, id: str) -> MetaDataItem:
        pass

    @abstractmethod
    async def delete_metadata(self, id: str):
        pass

    @abstractmethod
    async def fetch_video_id_list(self) -> List[str]:
        pass

    @abstractmethod
    async def fetch_video_url_list(self) -> List[str]:
        pass

    @abstractmethod
    async def fetch_newest_videos(self, last_id: str = None,
                                  filter_cond: FilterCondition = None) -> List[MetaDataItem]:
        pass