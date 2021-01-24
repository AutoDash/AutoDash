from ..data.MetaDataItem import MetaDataItem
from ..executor.iDatabaseExecutor import iDatabaseExecutor


# Not abstract, so a user can choose to default what database to interact with using this Executor
# Allows users to provide a list of IDs that the Source will pull and provide in order
class IteratorSource(iDatabaseExecutor):

    def __init__(self, parents=[], metadata_ids = []):
        super().__init__(parents, stateful=True)
        self.ids = metadata_ids

    def run(self) -> MetaDataItem:
        metadata_id = self.ids.pop(0)
        return self.database.fetch_metadata(metadata_id)

    def register_shared(self, manager):
        manager.register_executor('Source', self)

    def share(self, manager):
        return manager.Source()
