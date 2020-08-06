from ..database.LocalStorageAccessor import LocalStorageAccessor
from ..database.DataUpdater import DataUpdater


class LocalStorageUpdater(DataUpdater):

    def __init__(self, *parents):
        super().__init__(*parents)
        self.set_database(LocalStorageAccessor())
