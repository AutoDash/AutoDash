import asyncio

from ..data.MetaDataItem import MetaDataItem
from ..executor.iDatabaseExecutor import iDatabaseExecutor


# Not abstract, so a user can choose to default what database to interact with using this Executor
class DataUpdater(iDatabaseExecutor):

    def __init__(self, parents=None):
        super().__init__(parents)


    def run(self, metadata: MetaDataItem) -> MetaDataItem:
        if len(metadata.id) == 0 or metadata.id not in asyncio.run(self.database.fetch_video_id_list()):
            # metadata item is not in the database, therefore create it in the database
            asyncio.run(self.database.publish_new_metadata(metadata))
        else:
            asyncio.run(self.database.update_metadata(metadata))
        # Return saved metadata item
        return metadata
