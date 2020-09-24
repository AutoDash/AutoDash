from abc import ABC, abstractmethod
from typing import List

from ..data.FilterCondition import FilterCondition
from ..data.MetaDataItem import MetaDataItem

class AlreadyExistsException(Exception):
    '''Raise on adding a video that is already stored'''

class NotExistingException(Exception):
    '''Raise on accessing a video that does not exist in the database'''

class iReadOnlyDatabase(ABC):
    def __init__(self):
        super().__init__()

    # Used to create metadataItems from the dictionaries that databases return
    @staticmethod
    def create_metadata(id: str, var_dict: dict) -> MetaDataItem:
        var_dict['id'] = id
        defined_vars = var_dict.keys()

        for var in MetaDataItem.attributes():
            if var not in defined_vars:
                var_dict[var] = None

        return MetaDataItem(**var_dict)

    @abstractmethod
    def fetch_metadata(self, id: str) -> MetaDataItem:
        pass

    @abstractmethod
    def fetch_video_id_list(self) -> List[str]:
        pass

    @abstractmethod
    def fetch_video_url_list(self) -> List[str]:
        pass

    @abstractmethod
    def fetch_newest_videos(self, last_id: str = None,
                                  filter_cond: FilterCondition = None) -> List[MetaDataItem]:
        pass


class iDatabase(iReadOnlyDatabase):
    def __init__(self):
        super().__init__()

    # Sets the id of the metadata to a unique identifier
    @abstractmethod
    def publish_new_metadata(self, metadata: MetaDataItem) -> str:
        pass

    @abstractmethod
    def update_metadata(self, metadata: MetaDataItem):
        pass

    @abstractmethod
    def delete_metadata(self, id: str):
        pass
