from ..signals import CancelSignal
from ..data.VideoItem import VideoItem
from ..data.FilterCondition import FilterCondition
from .iExecutor import iExecutor


class Filterer(iExecutor):

    def __init__(self, *parents, filter_str: str = "tags['state'] != 'processed'"):
        super().__init__(*parents)

        self.filter_cond = FilterCondition(filter_str)


    def run(self, item: VideoItem):
        res = self.filter_cond.filter([item.metadata])

        if len(res) == 0:
            raise CancelSignal

        return item
