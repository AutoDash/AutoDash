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
    t: opens window for user customizable tags
    tab: Switch mode

Selection Mode: [NOT IN USE ANY MORE. ONLY USE MOUSE]
    m: Mark current location as accident location
    n: Toggle whether it is a dashcam video
        NOTE: by default, all videos will be dashcam
        Pressing n the first time will mark the video as not dashcam
    u: untag (Remove tags)
    ,: Remove the last marked accident location

BBox Mode:
    i: Select a new integer ID to work on, as will as cls. If ID already exists, will modify original
    r: reset current task
    c: Clear existing bounding boxes over frames
    v: Re-interpolate over frames [NOT implemented]
    b: Define bounding boxes over range
    u: Update class of current id based on popup input

Note:
    By default, video are assumed to be dashcam video

"""
from .gui_managers  import VideoPlayerGUIManager, VideoTaggingContext
from ..data.MetaDataItem import MetaDataItem

# Lets the user tag the file. Modifies MetaDataItem in place
def tag_file(file_loc, mdi:MetaDataItem):
    context = VideoTaggingContext(file_loc, None)
    gui = VideoPlayerGUIManager(context)
    gui.start()

    # mdi.accident_indexes = context.result.accident_frame_numbers
    # mdi.is_dashcam = context.result.is_dashcam
    bbox_fields = context.bbox_fields

    for key, val in context.result.additional_tags:
        mdi.add_tag(key, val)
    return mdi

def test():
    import sys
    tag_file(sys.argv[1], MetaDataItem(None, None, None, None))

if __name__ == "__main__":
    test()
