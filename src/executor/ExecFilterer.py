from typing import Union

from ..data.MetaDataItem import MetaDataItem
from ..signals import StopSignal
from ..data.VideoItem import VideoItem
from .iExecutor import iExecutor


class ExecFilterer(iExecutor):

    def __init__(self, *parents, filter_str: str = "data.tags.get('state') != 'processed'"):
        super().__init__(*parents)

        self.filter_str = filter_str
        self.filter_code = compile(filter_str, '<string>', 'eval')

    def run(self, item: Union[VideoItem, MetaDataItem]):
        metadata = self.get_metadata(item)

        res = eval(self.filter_code, {
            'data': metadata
        })

        if not res:
            print(f"Condition {self.filter_str} wasn't met")
            return None

        return item
