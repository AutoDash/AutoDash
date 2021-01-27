from abc import abstractmethod
from typing import Union, Any

from ..data.VideoItem import VideoItem
from ..data.MetaDataItem import MetaDataItem
from .iExecutor import iExecutor
from ..database.iDatabase import iDatabase


class UndefinedDatabaseException(Exception):
    '''Raise when attempt to access database before injected into the crawler'''


# Interface for any Executor that requires access to a database (either to make changes or get information)
class iDatabaseExecutor(iExecutor):
    def __init__(self, *parents, stateful=False):
        super().__init__(*parents, stateful=stateful)
        self.database = None

    def set_database(self, database: iDatabase):
        self.database = database
        return self

    @abstractmethod
    def run(self, item: Union[MetaDataItem, VideoItem]):
        pass

    def requires_database(self):
        return self.database is None
