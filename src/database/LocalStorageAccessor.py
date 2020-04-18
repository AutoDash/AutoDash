import uuid
from typing import List

import os

from src.data.MetaDataItem import MetaDataItem, metadata_from_file, gen_filename
from src.database.iDatabase import iDatabase, AlreadyExistsException, NotExistingException
from src.utils import get_project_root

METADATA_STORAGE_DIR = os.path.join(get_project_root(), "metadata_storage")

class LocalStorageAccessor(iDatabase):

    def __init__(self):
        if not os.path.exists(METADATA_STORAGE_DIR):
            os.mkdir(METADATA_STORAGE_DIR)

        self.url_list = []
        self.id_list = []
        for filename in os.listdir(METADATA_STORAGE_DIR):
            metadata = metadata_from_file(filename, METADATA_STORAGE_DIR)
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
        metadata.to_file(METADATA_STORAGE_DIR)

        self.id_list.append(metadata.id)
        self.url_list.append(metadata.url)
        return metadata.id

    async def update_metadata(self, metadata: MetaDataItem):
        if metadata.id not in self.id_list or metadata.url not in self.url_list:
            raise NotExistingException()

        # Overwrites existing file
        metadata.to_file(METADATA_STORAGE_DIR)

    async def fetch_metadata(self, id: str) -> MetaDataItem:
        if id not in self.id_list:
            raise NotExistingException()

        return metadata_from_file(gen_filename(id), METADATA_STORAGE_DIR)

    async def fetch_video_id_list(self) -> List[str]:
        return self.id_list

    async def fetch_video_url_list(self) -> List[str]:
        return self.url_list
