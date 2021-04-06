from ..database.FirestoreAccessor import FirestoreAccessor
from ..database.DataUpdater import DataUpdater
from typing import Union
from ..data.MetaDataItem import MetaDataItem
from ..data.VideoItem import VideoItem


class FirestoreUpdater(DataUpdater):
    def __init__(self, *parents):
        super().__init__(*parents)
        self.set_database(FirestoreAccessor())

    # temporarily override run so that we can easily do the migration. This will use the same id in firestore as firebase!!
    def run(
        self, item: Union[MetaDataItem,
                          VideoItem]) -> Union[MetaDataItem, VideoItem]:
        metadata = self.get_metadata(item)

        self.database.update_metadata(metadata)

        # Return saved metadata item
        return item
