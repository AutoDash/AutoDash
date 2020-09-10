import asyncio
from typing import Union

from ..signals import StopSignal
from ..data.VideoItem import VideoItem
from ..data.MetaDataItem import MetaDataItem
from ..executor.iDatabaseExecutor import iDatabaseExecutor


# Not abstract, so a user can choose to default what database to interact with using this Executor
class DataUpdater(iDatabaseExecutor):

    def __init__(self, parents=None):
        super().__init__(parents)


    def run(self, item: Union[MetaDataItem, VideoItem]) -> Union[MetaDataItem, VideoItem]:
        metadata = self.get_metadata(item)

        if metadata.id is None or len(metadata.id) == 0 or metadata.id not in asyncio.run(self.database.fetch_video_id_list()):
            if metadata.url in self.database.fetch_video_url_list():
                # The video already exists in the database, with a different id, so don't re-add it to the database
                raise StopSignal()
            # metadata item is not in the database, therefore create it in the database
            asyncio.run(self.database.publish_new_metadata(metadata))
        else:
            asyncio.run(self.database.update_metadata(metadata))
        # Return saved metadata item
        return item
