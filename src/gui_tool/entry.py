"""
Press h in GUI tool to see commands
"""
from .gui.bb_gui import BBGUIManager
from .gui.bb_context import BBContext
from ..data.MetaDataItem import MetaDataItem
from ..signals import CancelSignal
from .GUIExceptions import ManualTaggingAbortedException

# Lets the user tag the file. Modifies MetaDataItem in place
def tag_file(file_loc, mdi:MetaDataItem):
    while True:
        try:
            context = BBContext(file_loc, mdi.bb_fields)
            gui = BBGUIManager(context)
            gui.start()

            mdi.bb_fields = context.get_bbox_fields()

            for key, val in context.additional_tags:
                mdi.add_tag(key, val)

            if not context.is_dashcam:
                mdi.is_cancelled = True
                raise CancelSignal("Marked as not a dashcam video")

            return mdi

        except ManualTaggingAbortedException as e:
            print("Aborted. Will restart")
