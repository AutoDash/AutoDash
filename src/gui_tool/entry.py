"""
GUI TOOL CONTROLS
Navigation:
    a: 1 back
    s: 10 back
    d: 1 forward
    w: 10 forward
    space: pause/unpause

Tagging:
    m: Mark current location as accident location
    n: Not a dashcam video
        NOTE: by default, all videos will be dashcam
    t: opens window for user customizable tags
    u: untag (Remove tags)

Note:
    By default, video are assumed to be dashcam video

"""
from gui_tool.gui_managers import VideoPlayerGUIManager
from data.MetaDataItem import MetaDataItem

# Lets the user tag the file. Modifies MetaDataItem in place
def tag_file(file_loc, mdi:MetaDataItem):
    gui = VideoPlayerGUIManager(file_loc)
    res = gui.start()
    mdi.accident_index = res.accident_frame_number
    mdi.is_dashcam = res.is_dashcam

    for key, val in res.additional_tags:
        mdi.add_tag(key, val)

    return mdi
