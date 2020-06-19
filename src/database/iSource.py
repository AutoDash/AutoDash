from abc import abstractmethod
from typing import Dict, Any, List

from src.data.FilterCondition import FilterCondition
from src.data.MetaDataItem import MetaDataItem
from src.executor.iDatabaseExecutor import iDatabaseExecutor


class iSource(iDatabaseExecutor):

    @abstractmethod
    def __init__(self, *parents, last_id: str = None, cond: FilterCondition = None):
        super().__init__(*parents)
        self.last_id = last_id
        self.cond = cond

    def __load_data(self) -> List[MetaDataItem]:
        return self.database.fetch_newest_videos(self.last_id, self.cond)

    def run(self, obj: Dict[str, Any]) -> MetaDataItem:
        return self.__load_data()[0]