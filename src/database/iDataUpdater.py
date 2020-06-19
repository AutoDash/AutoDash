import asyncio

from src.data.MetaDataItem import MetaDataItem
from src.executor.iDatabaseExecutor import iDatabaseExecutor


class iDataUpdater(iDatabaseExecutor):

    def __init__(self, *parents):
        super().__init__(*parents)


    def run(self, metadata: MetaDataItem) -> MetaDataItem:
        if len(metadata.id) == 0 or metadata.id not in asyncio.run(self.database.fetch_video_id_list()):
            # metadata item is not in the database, therefore create it in the database
            asyncio.run(self.database.publish_new_metadata(metadata))
        else:
            asyncio.run(self.database.update_metadata(metadata))
        # Return saved metadata item
        return metadata

