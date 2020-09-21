from abc import abstractmethod
from typing import Any, Dict

from ..data.MetaDataItem import MetaDataItem
from ..executor.iDatabaseExecutor import iDatabaseExecutor, UndefinedDatabaseException


class CrawlerException(RuntimeError):
    '''Raise on inability to find next downloadable'''


class iCrawler(iDatabaseExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def next_downloadable(self) -> MetaDataItem:
        pass

    def check_new_url(self, url: str) -> bool:
        if self.database is None:
            raise UndefinedDatabaseException()

        urls = self.database.fetch_video_url_list()
        return url not in urls

    def run(self, obj : Dict[str, Any]):
        return self.next_downloadable()
