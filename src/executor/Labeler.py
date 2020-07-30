from gui_tool.entry import tag_file
from ..data.VideoItem import VideoItem
from .iExecutor import iExecutor


class Labeler(iExecutor):
    def run(self, item: VideoItem):
        tag_file(item.filepath, item.metadata)
        return item
