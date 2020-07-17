from typing import Dict, Any, List

from ..data.FilterCondition import FilterCondition
from ..data.MetaDataItem import MetaDataItem
from ..executor.iDatabaseExecutor import iDatabaseExecutor


# Not abstract, so a user can choose to default what database to interact with using this Executor
class Source(iDatabaseExecutor):

    def __init__(self, *parents, last_id: str = None, cond: FilterCondition = None):
        super().__init__(*parents, stateful=True)
        self.last_id = last_id
        self.cond = cond

        self.data = []

    def __load_data(self) -> List[MetaDataItem]:
        return self.database.fetch_newest_videos(self.last_id, self.cond)

    def run(self, obj: Dict[str, Any]) -> MetaDataItem:
        if not self.data:
            self.data = self.__load_data()
        return self.data.pop(0)
