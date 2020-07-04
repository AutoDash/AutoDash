import enum

from src.database.FirebaseAccessor import FirebaseAccessor
from src.database.LocalStorageAccessor import LocalStorageAccessor


class DatabaseConfigOption(enum.Enum):
    firebase = 1
    local = 2

def get_database(database_config: DatabaseConfigOption):
    if database_config is DatabaseConfigOption.firebase:
        database_access = FirebaseAccessor()
    else:
        database_access = LocalStorageAccessor()

    return database_access
