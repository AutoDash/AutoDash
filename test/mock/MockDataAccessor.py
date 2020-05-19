from typing import List

from src.data.MetaDataItem import MetaDataItem
from src.database.iDatabase import iDatabase, NotExistingException, AlreadyExistsException


class MockDataAccessor(iDatabase):

    def __init__(self):
        self.metadata_dict = {}

    async def publish_new_metadata(self, metadata: MetaDataItem) -> str:
        if id in self.metadata_dict.keys():
            raise AlreadyExistsException()
        await self.update_metadata(metadata)

    async def update_metadata(self, metadata: MetaDataItem):
        self.metadata_dict[metadata.id] = metadata

    async def fetch_metadata(self, id: str) -> MetaDataItem:
        if id not in self.metadata_dict.keys():
            raise NotExistingException()
        return self.metadata_dict[id]

    async def delete_metadata(self, id: str):
        if id not in self.metadata_dict.keys():
            raise NotExistingException()
        self.metadata_dict[id] = None

    async def fetch_video_id_list(self) -> List[str]:
        return list(self.metadata_dict.keys())

    async def fetch_video_url_list(self) -> List[str]:
        return list(map(lambda metadata: metadata.url, self.metadata_dict.values()))