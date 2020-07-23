from typing import List

from src.data.FilterCondition import FilterCondition
from src.data.MetaDataItem import MetaDataItem
from src.database.iDatabase import iDatabase, NotExistingException, AlreadyExistsException


class MockDataAccessor(iDatabase):

    def __init__(self):
        self.metadata_list = []

    async def publish_new_metadata(self, metadata: MetaDataItem) -> str:
        id = str(len(self.metadata_list))
        metadata.id = id
        self.metadata_list.append(metadata)
        return id

    async def update_metadata(self, metadata: MetaDataItem):
        self.metadata_list[int(metadata.id)] = metadata

    def fetch_metadata(self, id: str) -> MetaDataItem:
        if int(id) >= len(self.metadata_list):
            raise NotExistingException()
        return self.metadata_list[int(id)]

    async def delete_metadata(self, id: str):
        if int(id) >= len(self.metadata_list):
            raise NotExistingException()
        self.metadata_list[int(id)] = None

    def fetch_video_id_list(self) -> List[str]:
        id_list = []
        for i, metadata in enumerate(self.metadata_list):
            if metadata is not None:
                id_list.append(i)
        return id_list

    def fetch_video_url_list(self) -> List[str]:
        url_list = []
        for metadata in self.metadata_list:
            if metadata is not None:
                url_list.append(metadata.url)
        return url_list

    def fetch_newest_videos(self, last_id: str = None,
                                  filter_cond: FilterCondition = None) -> List[MetaDataItem]:
        if last_id is not None:
            metadata_list = self.metadata_list[int(last_id):]
        else:
            metadata_list = self.metadata_list

        metadata_list = list(filter(None, metadata_list))
        if filter_cond is not None:
            return filter_cond.filter(metadata_list)
        else:
            return metadata_list
