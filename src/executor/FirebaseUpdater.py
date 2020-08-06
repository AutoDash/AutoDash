from ..database import get_firebase_access
from ..database.DataUpdater import DataUpdater


class FirebaseUpdater(DataUpdater):

    def __init__(self, *parents):
        super().__init__(*parents)
        self.set_database(get_firebase_access())
