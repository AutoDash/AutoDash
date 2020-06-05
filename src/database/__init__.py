import enum

from .FirebaseAccessor import FirebaseAccessor
from .LocalStorageAccessor import LocalStorageAccessor


class DatabaseConfigOption(enum.Enum):
    firebase_metadata = 1
    local_storage_only = 2

#TODO: Update to read from config file, or replace this with singleton/dependency injection (whatever decided by pipeline)
DATABASE_CONFIG = DatabaseConfigOption.local_storage_only

if DATABASE_CONFIG is DatabaseConfigOption['firebase_metadata']:
    database_access = FirebaseAccessor()
else:
    database_access = LocalStorageAccessor()
