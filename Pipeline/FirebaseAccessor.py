import os, sys
from typing import List

import asyncio
import firebase_admin
from firebase_admin import credentials, db
from firebase_admin.db import Reference


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


def all_videos_reference():
    return db.reference('all_videos')


def excluded_videos_reference():
    return db.reference('excluded_videos')


async def query_list(ref: Reference) -> List[str]:
    vals = ref.get()
    if vals is None:
        return []

    result = []
    for key, val in vals.items():
        result.append(val)
    return result


async def add_video_url(url: str) -> str:
    # Check that the video isn't already in the list
    video_ref = all_videos_reference()
    existing_list = await query_list(video_ref)
    if url in existing_list:
        return ""

    return video_ref.push(url).key


async def fetch_video_list():
    video_ref = all_videos_reference()
    return await query_list(video_ref)


async def add_excluded_video(url: str) -> str:
    # Check that the video isn't already in the list
    excluded_ref = excluded_videos_reference()
    existing_list = await query_list(excluded_ref)
    if url in existing_list:
        return ""

    return excluded_ref.push(url).key


async def fetch_excluded_video_list() -> List[str]:
    excluded_ref = excluded_videos_reference()
    return await query_list(excluded_ref)
