from typing import Union

from ..data.MetaDataItem import MetaDataItem
from ..signals import DeleteSignal
from ..data.VideoItem import VideoItem
from .iExecutor import iExecutor


class DatabaseCleaner(iExecutor):

    def __init__(self, *parents):
        super().__init__(*parents)

    def run(self, item: Union[VideoItem, MetaDataItem]):
        metadata = self.get_metadata(item)

        if metadata.to_be_deleted:
            raise DeleteSignal

        return item
