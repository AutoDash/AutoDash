from typing import Iterator

from ..data.FilterCondition import FilterCondition
from ..data.MetaDataItem import MetaDataItem
from ..executor.iDatabaseExecutor import iDatabaseExecutor


# Not abstract, so a user can choose to default what database to interact with using this Executor
class Source(iDatabaseExecutor):

    def __init__(self, parents=[], last_id: str = None, filter_str: str = None):
        super().__init__(parents, stateful=True)
        self.last_id = last_id

        if filter_str is None:
            self.cond = None
        else:
            self.cond = FilterCondition(filter_str)

        self.data = None

    def __load_data(self, cond) -> Iterator[MetaDataItem]:
        # Prioritize passed-in filter condition over class cond
        if cond is None:
            cond = self.cond
        return self.database.fetch_newest_videos(self.last_id, cond)

    def run(self, cond: FilterCondition = None) -> MetaDataItem:
        if not self.data:
            self.data = self.__load_data(cond)
        return next(self.data)

    def register_shared(self, manager):
        manager.register_executor('Source', self)

    def share(self, manager):
        return manager.Source()
