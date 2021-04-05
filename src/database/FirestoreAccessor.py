import os
from typing import Iterator, List

import firebase_admin
from firebase_admin import credentials
from firebase_admin.firestore import client
from google.cloud import firestore

from ..data.FilterCondition import FilterCondition
from ..data.MetaDataItem import MetaDataItem
from .iDatabase import iDatabase, AlreadyExistsException, NotExistingException
from ..utils import get_project_root
from .FirebaseAccessor import FirebaseAccessor


FIREBASE_CRED_FILENAME = "autodash-9dccb-add3cdae62ea.json"

# Raised if trying to instantiate Firebase Accessor without
class MissingCredentials(Exception):
    pass


class FirestoreAccessor(iDatabase):

    initialized = False

    # Must be initialized only once
    def initial_firebase(self):
        dirname = get_project_root()
        cred_file = os.path.join(dirname, "autodash-9dccb-add3cdae62ea.json")
        

        if os.path.exists(cred_file):
            # Have write access to Firebase
            cred = credentials.Certificate(cred_file)
            fb_app = firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://autodash-9dccb.firebaseio.com/',
                'databaseAuthVariableOverride': {
                    'uid': 'pipeline-worker'
                }
            })
        else:
            raise MissingCredentials()


    def __init__(self):
        if not FirestoreAccessor.initialized and not FirebaseAccessor.initialized:
            self.initial_firebase()
            FirestoreAccessor.initialized = True
        self.client = client(firebase_admin.get_app())
    
    def fetch_next_metadata(self):
        ref = self.__metadata_reference()
        items = ref.stream()
        for item in items:
            yield self.create_metadata(item.to_dict())

    def __metadata_reference(self):
        return self.client.collection("metadata")


    def fetch_video_url_list(self) -> List[str]:
        pass

    def fetch_all_metadata(self) -> List[dict]:
        pass

    def fetch_video_id_list(self) -> List[str]:
        pass


    def fetch_newest_videos(self, last_timestamp: int = 0,
                                  filter_cond: FilterCondition = None) -> Iterator[MetaDataItem]:
        ref = self.__metadata_reference()

        dict_stream = ref.where("date_created", ">", last_timestamp).order_by("date_created", direction=firestore.Query.DESCENDING).stream()
        md_stream = (self.create_metadata(d.id, d.to_dict()) for d in dict_stream)
        if not filter_cond:
            return md_stream
        else :
            return (x for x in md_stream if filter_cond.filter([x]))

    def publish_new_metadata(self, metadata: MetaDataItem) -> str:
        ref = self.__metadata_reference()

        if not metadata.is_split_url:
            if ref.where("url", "==", metadata.url).limit(1).get():
                raise AlreadyExistsException("Error, video url already in list")

        doc = ref.add(metadata.to_json())
        metadata.id = doc.id
        return doc.id

    
    def metadata_exists(self, metadata: MetaDataItem) -> bool:
        ref = self.__metadata_reference()
        return ref.document(metadata.id).exists


    def update_metadata(self, metadata: MetaDataItem):
        ref = self.__metadata_reference()

        # if not self.metadata_exists(metadata.id):
        #     raise NotExistingException()

        ref.document(metadata.id).set(metadata.to_json())


    def fetch_metadata(self, id: str) -> MetaDataItem:
        print("fetch metadata")
        ref = self.__metadata_reference()

        doc = ref.document(id)
        if not doc.exists:
            raise NotExistingException()
        
        print("doc exists")

        return self.create_metadata(id, doc.to_dict())

    
    def metadata_exists(self, id: str) -> bool:
        return self.__metadata_reference().document(id).get().exists
    
    def url_exists(self, url: str) -> bool:
        ref = self.__metadata_reference()

        return len(list(ref.where("url", "==", url).limit(1).get())) > 0

    def delete_metadata(self, id: str):
        ref = self.__metadata_reference()

        doc = ref.document(id)
        if not doc.exists:
            raise NotExistingException()

        doc.delete()
