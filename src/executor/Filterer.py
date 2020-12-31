from typing import Union

from ..data.MetaDataItem import MetaDataItem
from ..signals import StopSignal
from ..data.VideoItem import VideoItem
from ..data.FilterCondition import FilterCondition
from .iExecutor import iExecutor


class Filterer(iExecutor):

    def __init__(self, *parents, filter_str: str = "state != 'processed'"):
        super().__init__(*parents)

        self.filter_cond = FilterCondition(filter_str)


    def run(self, item: Union[VideoItem, MetaDataItem]):
        metadata = self.get_metadata(item)

        res = self.filter_cond.filter([metadata])

        if len(res) == 0:
            print(f"Condition {self.filter_cond} wasn't met")
            return None

        return item
