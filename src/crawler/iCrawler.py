from abc import ABC, abstractmethod

from src.data.MetaDataItem import MetaDataItem

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
        if self.database is None:
            raise UndefinedDatabaseException()

        urls = await self.database.fetch_video_url_list()
        return url not in urls


    #helper method to publish item to database
    async def publish_metadata(self, item:MetaDataItem):
        if self.database is None:
            raise UndefinedDatabaseException()

        await self.database.publish_new_metadata(item)
