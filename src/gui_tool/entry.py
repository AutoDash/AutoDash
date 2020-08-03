"""
Press h in GUI tool to see commands
"""
from gui_tool.gui_managers import VideoPlayerGUIManager
from gui_tool.VideoTaggingContext import VideoTaggingContext
from data.MetaDataItem import MetaDataItem
from signals import CancelSignal
from gui_tool.GUIExceptions import ManualTaggingAbortedException

# Lets the user tag the file. Modifies MetaDataItem in place
def tag_file(file_loc, mdi:MetaDataItem):
    while True:
        try:
            context = VideoTaggingContext(file_loc, (
                mdi.bb_frames,
                mdi.bb_ids,
                mdi.bb_clss,
                mdi.bb_x1s,
                mdi.bb_y1s,
                mdi.bb_x2s,
                mdi.bb_y2s,
                mdi.bb_has_accident,
            ))
            gui = VideoPlayerGUIManager(context)
            gui.start()

            bbox_fields = context.get_bbox_fields()
            frames, ids, clss, x1s, y1s, x2s, y2s, selected = bbox_fields
            mdi.bb_frames = frames
            mdi.bb_ids = ids
            mdi.bb_clss = clss
            mdi.bb_x1s = x1s
            mdi.bb_y1s = y1s
            mdi.bb_x2s = x2s
            mdi.bb_y2s = y2s
            mdi.bb_has_accident = selected

            for key, val in context.additional_tags:
                mdi.add_tag(key, val)

            if not context.is_dashcam:
                mdi.is_cancelled = True
                raise CancelSignal("Marked as not a dashcam video")

            return mdi

        except ManualTaggingAbortedException as e:
            print("Aborted. Will restart")

def test():
    import sys
    mdi = MetaDataItem(**{"title": None, "download_src": None, "url": None})
    tag_file(sys.argv[1], mdi)
    print(mdi)

if __name__ == "__main__":
    test()
