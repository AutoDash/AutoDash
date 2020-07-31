from typing import List

import requests

from ..data.FilterCondition import FilterCondition
from ..data.MetaDataItem import MetaDataItem
from .iDatabase import iReadOnlyDatabase

firebase_url = 'https://autodash-9dccb.firebaseio.com/metadata'

class ReadOnlyFirebaseAccessor(iReadOnlyDatabase):
    def __init__(self):
        super().__init__()

    def fetch_metadata(self, id: str) -> MetaDataItem:
        res = requests.get(firebase_url+'/'+id+".json")
        return self.create_metadata(id, res.json())

    def fetch_video_id_list(self) -> List[str]:
        res = requests.get(firebase_url + ".json", params={'shallow':'true'})
        return list(res.json().keys())

    def fetch_video_url_list(self) -> List[str]:
        ids = self.fetch_video_id_list()
        urls = []
        for id in ids:
            metadata = self.fetch_metadata(id)
            urls.append(metadata.url)
        return urls

    def fetch_newest_videos(self, last_id: str = None,
                                  filter_cond: FilterCondition = None) -> List[MetaDataItem]:
        ids = reversed(self.fetch_video_id_list())
        metadata_items = []

        for id in ids:
            if id == last_id:
                break
            metadata_items.append(self.fetch_metadata(id))

        if filter_cond is not None:
            metadata_items = filter_cond.filter(metadata_items)

        return metadata_items
