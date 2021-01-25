from ..database import get_firebase_access
from ..database.IteratorSource import IteratorSource


class IteratorFirebaseSource(IteratorSource):

    def __init__(self, parents, metadata_ids=[]):
        super().__init__(parents, metadata_ids)
        self.set_database(get_firebase_access())

    def register_shared(self, manager):
        manager.register_executor('FirebaseSource', self)

    def share(self, manager):
        return manager.FirebaseSource()
