import os, sys
from typing import List

import firebase_admin
from firebase_admin import credentials, db
from firebase_admin.db import Reference

from src.data.MetaDataItem import MetaDataItem


def setup():
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    cred_file = os.path.join(dirname, "autodash-9dccb-firebase-adminsdk-si4cw-43915a72e5.json")

    cred = credentials.Certificate(cred_file)
    fb_app = firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://autodash-9dccb.firebaseio.com/',
        'databaseAuthVariableOverride': {
            'uid': 'pipeline-worker'
        }
    })

def create_metadata(id: str, var_dict: dict) -> MetaDataItem:
    # Find all needed variables of MetadataItem
    empty_item = MetaDataItem(None, None, None, None, None, None)
    all_vars = empty_item.to_json().keys()

    var_dict['id'] = id
    defined_vars = var_dict.keys()

    for var in all_vars:
        if var not in defined_vars:
            var_dict[var] = None


    return MetaDataItem(**var_dict)


def metadata_reference():
    return db.reference('metadata')


async def query_list(ref: Reference) -> List[str]:
    vals = ref.get()
    if vals is None:
        return []

    result = []
    for key, val in vals.items():
        result.append(val)
    return result


async def query_keys(ref: Reference) -> List[str]:
    vals = ref.get()
    if vals is None:
        return []

    keys = []
    for key, val in vals.items():
        keys.append(key)
    return keys


async def fetch_video_url_list() -> List[str]:
    ref = metadata_reference()
    metadata_list = await query_list(ref)
    urls = map(lambda metadata: metadata['url'], metadata_list)
    return list(urls)


async def fetch_video_id_list() -> List[str]:
    ref = metadata_reference()
    return await query_keys(ref)


async def fetch_newest_videos(last_id: str) -> List[MetaDataItem]:
    metadata_ref = metadata_reference()

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
        result.append(create_metadata(key, val))

    return result


async def publish_new_metadata(metadata: MetaDataItem) -> str:
    ref = metadata_reference()

    # Check that the video isn't already in the list by seeing if its url is already in the list
    existing_list = await fetch_video_url_list()
    if metadata.url in existing_list:
        return "Error, video url already in list"

    return ref.push(metadata.to_json()).key


# Returns 1 on Success and 0 on Failure
async def update_metadata(metadata: MetaDataItem) -> int:
    ref = metadata_reference()

    existing_ids = await query_keys(ref)
    if metadata.id not in existing_ids:
        return 0

    ref.child(metadata.id).update(metadata.to_json())
    return 1


async def fetch_metadata(id: str) -> MetaDataItem:
    metadata_ref = metadata_reference()
    item_dict = metadata_ref.child(id).get()
    return create_metadata(id, dict(item_dict))