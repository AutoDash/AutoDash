from src.database import FirebaseAccessor
from src.database.iSource import iSource


class FirebaseSource(iSource):

    def __init__(self):
        super().__init__()
        self.set_database(FirebaseAccessor())
