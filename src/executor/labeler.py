from gui_tool.entry import tag_file
from data.VideoItem import VideoItem
from executor.iExecutor import iExecutor


class Labeler(iExecutor):
    def run(self, item: VideoItem):
        print("label!!!")
        tag_file(item.filepath, item.metadata)
        return item
