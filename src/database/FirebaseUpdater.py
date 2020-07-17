from .FirebaseAccessor import FirebaseAccessor
from .DataUpdater import DataUpdater


class FirebaseUpdater(DataUpdater):

    def __init__(self, *parents):
        super().__init__(*parents)
        self.set_database(FirebaseAccessor())
