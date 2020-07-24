from abc import abstractmethod
from typing import Any, Dict

import asyncio

from src.data.MetaDataItem import MetaDataItem
from src.executor.iDatabaseExecutor import iDatabaseExecutor, UndefinedDatabaseException


class CrawlerException(RuntimeError):
    '''Raise on inability to find next downloadable'''


class iCrawler(iDatabaseExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    async def next_downloadable(self) -> MetaDataItem:
        pass

    async def check_new_url(self, url: str) -> bool:
        if self.database is None:
            raise UndefinedDatabaseException()

        urls = self.database.fetch_video_url_list()
        return url not in urls

    def run(self, obj : Dict[str, Any]):
        return asyncio.run(self.next_downloadable())
