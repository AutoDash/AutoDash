from src.database.FirebaseAccessor import FirebaseAccessor
from src.database.iDataUpdater import iDataUpdater


class FirebaseUpdater(iDataUpdater):

    def __init__(self, *parents):
        super().__init__(*parents)
        self.set_database(FirebaseAccessor())
