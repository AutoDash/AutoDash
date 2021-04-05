from ..database.FirestoreAccessor import FirestoreAccessor
from ..database.DataUpdater import DataUpdater


class FirestoreUpdater(DataUpdater):

    def __init__(self, *parents):
        super().__init__(*parents)
        self.set_database(FirestoreAccessor())
