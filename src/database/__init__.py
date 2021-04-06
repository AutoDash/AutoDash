import enum
import os

from ..utils import get_project_root
from .FirebaseAccessor import FirebaseAccessor, FIREBASE_CRED_FILENAME
from .ReadOnlyFirebaseAccessor import ReadOnlyFirebaseAccessor
from .LocalStorageAccessor import LocalStorageAccessor
from .FirestoreAccessor import FirestoreAccessor

class DatabaseConfigOption(enum.Enum):
    firebase = 1
    local = 2
    firestore = 3

def get_firebase_access():
    dirname = get_project_root()
    cred_file = os.path.join(dirname, FIREBASE_CRED_FILENAME)

    if os.path.exists(cred_file):
        return FirebaseAccessor()
    else:
        return ReadOnlyFirebaseAccessor()

def get_database(database_config: DatabaseConfigOption):
    if database_config is DatabaseConfigOption.local:
        database_access = LocalStorageAccessor()
    elif database_config is DatabaseConfigOption.firestore:
        database_access = FirestoreAccessor()
    else:
        database_access = get_firebase_access()

    return database_access
