import enum
import os

from utils import get_project_root
from database.FirebaseAccessor import FirebaseAccessor, FIREBASE_CRED_FILENAME
from database.ReadOnlyFirebaseAccessor import ReadOnlyFirebaseAccessor
from database.LocalStorageAccessor import LocalStorageAccessor


class DatabaseConfigOption(enum.Enum):
    firebase = 1
    local = 2

def get_firebase_access():
    dirname = get_project_root()
    cred_file = os.path.join(dirname, FIREBASE_CRED_FILENAME)

    if os.path.exists(cred_file):
        return FirebaseAccessor()
    else:
        return ReadOnlyFirebaseAccessor()

def get_database(database_config: DatabaseConfigOption):
    if database_config is DatabaseConfigOption.firebase:
        database_access = get_firebase_access()
    else:
        database_access = LocalStorageAccessor()

    return database_access
