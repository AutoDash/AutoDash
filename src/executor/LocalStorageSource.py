from ..database.LocalStorageAccessor import LocalStorageAccessor
from ..database.Source import Source


class LocalStorageSource(Source):

    def __init__(self, *parents, last_id: str = None, filter_str: str = None):
        super().__init__(*parents, last_id, filter_str)
        self.set_database(LocalStorageAccessor())

    def register_shared(self, manager):
        manager.register_executor('LocalStorageSource', self)

    def share(self, manager):
        return manager.LocalStorageSource()
