import uuid
from typing import List

import os

from data.FilterCondition import FilterCondition
from data.MetaDataItem import MetaDataItem, metadata_from_file, gen_filename, delete_metadata_file
from .iDatabase import iDatabase, AlreadyExistsException, NotExistingException
from utils import get_project_root

METADATA_STORAGE_DIR = os.path.join(get_project_root(), "metadata_storage")

class LocalStorageAccessor(iDatabase):

    # Allow setting the storage location so that tests can run on a separate
    #  directory and not break anything in the production database folder
    def __init__(self, storage_loc = METADATA_STORAGE_DIR):
        self.storage_loc = storage_loc
        if not os.path.exists(self.storage_loc):
            os.mkdir(self.storage_loc)

        self.url_list = []
        self.id_list = []
        for filename in os.listdir(self.storage_loc):
            metadata = metadata_from_file(filename, self.storage_loc)
            self.url_list.append(metadata.url)
            self.id_list.append(metadata.id)

    def __gen_new_id(self) -> str:
        new_id = uuid.uuid4()
        while new_id in self.id_list:
            new_id = uuid.uuid4()
        return str(new_id)

    async def publish_new_metadata(self, metadata: MetaDataItem) -> str:
        if metadata.url in self.url_list:
            raise AlreadyExistsException()

        metadata.id = self.__gen_new_id()
        metadata.to_file(self.storage_loc)

        self.id_list.append(metadata.id)
        self.url_list.append(metadata.url)
        return metadata.id

    async def update_metadata(self, metadata: MetaDataItem):
        if metadata.id not in self.id_list or metadata.url not in self.url_list:
            raise NotExistingException()

        # Overwrites existing file
        metadata.to_file(self.storage_loc)

    def fetch_metadata(self, id: str) -> MetaDataItem:
        if id not in self.id_list:
            raise NotExistingException()

        return metadata_from_file(gen_filename(id), self.storage_loc)

    async def delete_metadata(self, id: str):
        if id not in self.id_list:
            raise NotExistingException()

        delete_metadata_file(id, self.storage_loc)

    def fetch_video_id_list(self) -> List[str]:
        return self.id_list

    def fetch_video_url_list(self) -> List[str]:
        return self.url_list

    def fetch_newest_videos(self, last_id: str = None,
                                  filter_cond: FilterCondition = None) -> List[MetaDataItem]:
        result = []
        for id in reversed(self.fetch_video_id_list()):
            if id == last_id:
                break
            result.append(self.fetch_metadata(id))

        if filter_cond is not None:
            result = filter_cond.filter(result)

        return result
