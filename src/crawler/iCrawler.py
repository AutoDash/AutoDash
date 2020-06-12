from abc import abstractmethod
from typing import Any, Dict

import asyncio

from src.data.MetaDataItem import MetaDataItem
from src.executor.iExecutor import iExecutor


class CrawlerException(Exception):
    '''Raise on inability to find next downloadable'''

class UndefinedDatabaseException(Exception):
    '''Raise when attempt to access database before injected into the crawler'''

class iCrawler(iExecutor):
    def __init__(self, *parents):
        super().__init__(*parents)

    @abstractmethod
    async def next_downloadable(self) -> MetaDataItem:
        pass

    async def check_new_url(self, url: str) -> bool:
        if self.database is None:
            raise UndefinedDatabaseException()

        urls = await self.database.fetch_video_url_list()
        return url not in urls

    def run(self, obj : Dict[str, Any]):
        return asyncio.run(self.next_downloadable())
