import enum

from src.database.FirebaseAccessor import FirebaseAccessor


class DatabaseConfigOption(enum.Enum):
    firebase_metadata = 1
    local_storage_only = 2

#TODO: Update to read from config file
DATABASE_CONFIG = DatabaseConfigOption.firebase_metadata

if DATABASE_CONFIG is DatabaseConfigOption['firebase_metadata']:
    database_access = FirebaseAccessor()
else:
    database_access = LocalAccessor