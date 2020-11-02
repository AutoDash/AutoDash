from ..gui_tool.entry import split_file
from ..data.VideoItem import VideoItem
from .iExecutor import iExecutor

class Splitter(iExecutor):
    def run(self, item: VideoItem):
        items = split_file(item.filepath, item.metadata)
        return items
