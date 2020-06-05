"""
TAGGING GUI CONTROLS
Navigation:
    a:     1 back
    s:     10 back
    d:     1 forward
    w:     10 forward
    Space: Pause/unpause
    Enter: Finish and continue
    Esc:   Abort. Will raise ManualTaggingAbortedException

Tagging:
    m: Mark current location as accident location
    n: Toggle whether it is a dashcam video
        NOTE: by default, all videos will be dashcam
        Pressing n the first time will mark the video as not dashcam
    t: opens window for user customizable tags
    u: untag (Remove tags)
    ,: Remove the last marked accident location

REVIEW GUI CONTROLS
    Enter:     Approve and continue
    Backspace: Reject and redo
    Esc:       Abort. Will raise ManualTaggingAbortedException
    aswd:      Works the same way as in the tagging UI

Note:
    By default, video are assumed to be dashcam video

"""
from .gui_managers  import VideoPlayerGUIManager, VideoTaggingContext
from ..data.MetaDataItem import MetaDataItem

# Lets the user tag the file. Modifies MetaDataItem in place
def tag_file(file_loc, mdi:MetaDataItem):
    context = VideoTaggingContext(file_loc)
    gui = VideoPlayerGUIManager(context)
    gui.start()

    if context.result.marked:
        mdi.accident_indexes = context.result.accident_frame_numbers
        mdi.is_dashcam = context.result.is_dashcam

    for key, val in context.result.additional_tags:
        mdi.add_tag(key, val)
    return mdi

def test():
    import sys
    tag_file(sys.argv[1], MetaDataItem(None, None, None, None))

if __name__ == "__main__":
    test()
