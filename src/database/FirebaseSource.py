from . import get_firebase_access
from .Source import Source


class FirebaseSource(Source):

    def __init__(self, *parents, last_id: str = None, cond: FilterCondition = None):
        super().__init__(*parents, last_id, cond)
        self.set_database(get_firebase_access())
