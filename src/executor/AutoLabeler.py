from ..data.VideoItem import VideoItem
from .iExecutor import iExecutor

# Used to tag every in pipeline with the same value, so that they can be later filtered to not be processed again
class AutoLabeler(iExecutor):
    def __init__(self, *parents, val="processed", key="state"):
        super().__init__(*parents)
        self.key = key
        self.val = val

    def run(self, item: VideoItem):
        item.metadata.add_tag(self.key, self.val)
        return item
