from .LocalStorageAccessor import LocalStorageAccessor
from .Source import Source


class LocalStorageSource(Source):

    def __init__(self, *parents, last_id: str = None, filter_str: str = None):
        super().__init__(*parents, last_id, filter_str)
        self.set_database(LocalStorageAccessor())
