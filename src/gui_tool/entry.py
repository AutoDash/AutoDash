"""
GUI TOOL CONTROLS
Navigation:
    a: 1 back
    s: 10 back
    d: 1 forward
    w: 10 forward
    space: pause/unpause

Tagging:
    m: Tag the current location as accident location
    n: Tag the video as not a dashcam video
    b: Remove tagging

Note:
    By default, video are assumed to be dashcam video
    For now, if it actually is dashcam video is ignored. There is no field in MetaDataItem

"""
from src.gui_tool.gui_managers import VideoPlayerGUIManager
from src.data.MetaDataItem import MetaDataItem

# Lets the user tag the file. Modifies MetaDataItem in place
def tag_file(file_loc, mdi:MetaDataItem):
    gui = VideoPlayerGUIManager(file_loc)
    res = gui.start()
    mdi.location = res.accident_frame_number
    return mdi

