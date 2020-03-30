from abc import ABC, abstractmethod

from src.data.MetaDataItem import MetaDataItem
from src.FirebaseAccessor import fetch_video_url_list

class CrawlerException(Exception):
    '''Raise on inability to find next downloadable'''

class UndefinedDatabaseException(Exception):
    '''Raise when attempt to access database before injected into the crawler'''

class iCrawler(ABC):
    def __init__(self):
        self.database = None
        super().__init__

    @abstractmethod
    async def next_downloadable(self) -> MetaDataItem:
        pass

    def set_database(self, database):
        self.database = database

    async def check_new_url(self, url: str) -> bool:
        urls = await fetch_video_url_list()
        return url not in urls

    #helper method to publish item to firebase, REMOVE
    def publish_firebase(self, item:MetaDataItem):
        pass
