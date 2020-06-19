from src.database.FirebaseAccessor import FirebaseAccessor
from src.database.iSource import iSource


class FirebaseSource(iSource):

    def __init__(self, *parents):
        super().__init__(*parents)
        self.set_database(FirebaseAccessor())
