from .LocalStorageAccessor import LocalStorageAccessor
from .Source import Source


class LocalStorageSource(Source):

    def __init__(self, *parents):
        super().__init__(*parents)
        self.set_database(LocalStorageAccessor())
