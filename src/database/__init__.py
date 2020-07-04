import enum
import os

from utils import get_project_root
from .FirebaseAccessor import FirebaseAccessor, FIREBASE_CRED_FILENAME
from .ReadOnlyFirebaseAccessor import ReadOnlyFirebaseAccessor
from .LocalStorageAccessor import LocalStorageAccessor


class DatabaseConfigOption(enum.Enum):
    firebase_metadata = 1
    local_storage_only = 2

def get_firebase_access():
    dirname = get_project_root()
    cred_file = os.path.join(dirname, FIREBASE_CRED_FILENAME)

    if os.path.exists(cred_file):
        return FirebaseAccessor()
    else:
        return ReadOnlyFirebaseAccessor()


#TODO: Update to read from config file, or replace this with singleton/dependency injection (whatever decided by pipeline)
DATABASE_CONFIG = DatabaseConfigOption.local_storage_only

if DATABASE_CONFIG is DatabaseConfigOption['firebase_metadata']:
    database_access = get_firebase_access()
else:
    database_access = LocalStorageAccessor()
