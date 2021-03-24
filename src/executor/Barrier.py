from typing import Union

from ..data.MetaDataItem import MetaDataItem
from ..signals import BarrierSignal
from ..data.VideoItem import VideoItem
from .iExecutor import iExecutor


class Barrier(iExecutor):

    def __init__(self, *parents):
        super().__init__(*parents)

    def run(self, item: Union[VideoItem, MetaDataItem]):
        raise BarrierSignal
