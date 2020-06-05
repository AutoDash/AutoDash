from abc import abstractmethod
from typing import Any, Dict

import asyncio

from ..data.MetaDataItem import MetaDataItem
from ..executor.iExecutor import iExecutor


class CrawlerException(Exception):
    '''Raise on inability to find next downloadable'''

class UndefinedDatabaseException(Exception):
    '''Raise when attempt to access database before injected into the crawler'''

class iCrawler(iExecutor):
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

    def run(self, obj : Dict[str, Any]):
        metadata_item = asyncio.run(self.next_downloadable())
        asyncio.run(self.publish_metadata(metadata_item))
