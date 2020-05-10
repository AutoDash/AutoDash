import os
from typing import List

import firebase_admin
from firebase_admin import credentials, db
from firebase_admin.db import Reference

from src.data.MetaDataItem import MetaDataItem
from src.database.iDatabase import iDatabase, AlreadyExistsException, NotExistingException
from src.utils import get_project_root


class FirebaseAccessor(iDatabase):

    initialized = False

    # Must be initialized only once
    def initial_firebase(self):
        dirname = get_project_root()
        cred_file = os.path.join(dirname, "autodash-9dccb-add3cdae62ea.json")

        cred = credentials.Certificate(cred_file)
        fb_app = firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://autodash-9dccb.firebaseio.com/',
            'databaseAuthVariableOverride': {
                'uid': 'pipeline-worker'
            }
        })

    def __init__(self):
        if not FirebaseAccessor.initialized:
            self.initial_firebase()
            FirebaseAccessor.initialized = True

    def __create_metadata(self, id: str, var_dict: dict) -> MetaDataItem:
        var_dict['id'] = id
        defined_vars = var_dict.keys()

        for var in MetaDataItem.attributes():
            if var not in defined_vars:
                var_dict[var] = None

        tags = var_dict.pop('tags', None)
        if tags is None:
            tags = {}

        metadata_item = MetaDataItem(**var_dict)

        for name, tag in tags.items():
            metadata_item.add_tag(name, tag)

        return metadata_item

    def __metadata_reference(self):
        return db.reference('metadata')

    async def __query_list(self, ref: Reference) -> List[str]:
        vals = ref.get()
        if vals is None:
            return []

        result = []
        for key, val in vals.items():
            result.append(val)
        return result

    async def __query_keys(self, ref: Reference) -> List[str]:
        vals = ref.get()
        if vals is None:
            return []

        keys = []
        for key, val in vals.items():
            keys.append(key)
        return keys


    async def fetch_video_url_list(self) -> List[str]:
        ref = self.__metadata_reference()
        metadata_list = await self.__query_list(ref)
        urls = map(lambda metadata: metadata['url'], metadata_list)
        return list(urls)


    async def fetch_video_id_list(self) -> List[str]:
        ref = self.__metadata_reference()
        return await self.__query_keys(ref)


    async def fetch_newest_videos(self, last_id: str) -> List[MetaDataItem]:
        metadata_ref = self.__metadata_reference()

        # Keys are timestamp based and therefore ordering them by key gets them in the order they were added
        vals = metadata_ref.order_by_key().get()
        if vals is None:
            return []

        # Reversing this ordered list will put the newest items first, and therefore
        # all the items seen before the recognized last item are new
        result = []
        for key, val in reversed(vals.items()):
            if key == last_id:
                break
            result.append(self.__create_metadata(key, val))

        return result


    async def publish_new_metadata(self, metadata: MetaDataItem) -> str:
        ref = self.__metadata_reference()

        # Check that the video isn't already in the list by seeing if its url is already in the list
        existing_list = await self.fetch_video_url_list()
        if metadata.url in existing_list:
            raise AlreadyExistsException("Error, video url already in list")

        key = ref.push(metadata.to_json()).key
        metadata.id = key
        return key


    async def update_metadata(self, metadata: MetaDataItem):
        ref = self.__metadata_reference()

        existing_ids = await self.__query_keys(ref)
        if metadata.id not in existing_ids:
            raise NotExistingException()

        ref.child(metadata.id).update(metadata.to_json())


    async def fetch_metadata(self, id: str) -> MetaDataItem:
        ref = self.__metadata_reference()

        existing_ids = await self.__query_keys(ref)
        if id not in existing_ids:
            raise NotExistingException()

        item_dict = ref.child(id).get()
        return self.__create_metadata(id, dict(item_dict))


    async def delete_metadata(self, id: str):
        ref = self.__metadata_reference()

        existing_ids = await self.__query_keys(ref)
        if id not in existing_ids:
            raise NotExistingException()

        ref.child(id).delete()
