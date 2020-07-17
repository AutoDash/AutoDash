from . import get_firebase_access
from .DataUpdater import DataUpdater


class FirebaseUpdater(DataUpdater):

    def __init__(self, *parents):
        super().__init__(*parents)
        self.set_database(get_firebase_access())
