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
    n: Not a dashcam video
        NOTE: by default, all videos will be dashcam
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
from src.gui_tool.gui_managers import VideoPlayerGUIManager, VideoTaggingContext, VisualizeTaggingResultsGUIManager
from src.data.MetaDataItem import MetaDataItem

# Lets the user tag the file. Modifies MetaDataItem in place
def tag_file(file_loc, mdi:MetaDataItem):
    tagging_results_approved = False

    while not tagging_results_approved:
        context = VideoTaggingContext(file_loc)
        gui = VideoPlayerGUIManager(context)
        gui.start()

        confirmation_gui = VisualizeTaggingResultsGUIManager(context)
        tagging_results_approved = confirmation_gui.start()

    if context.result.marked:
        mdi.accident_indexes = context.result.accident_frame_numbers
        mdi.is_dashcam = context.result.is_dashcam
    return mdi