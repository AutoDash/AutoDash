"""
Press h in GUI tool to see commands
"""
from tkinter import Tk

from .gui.bb_gui import BBGUIManager
from .gui.bb_context import BBContext
from ..data.MetaDataItem import MetaDataItem
from ..signals import CancelSignal
from .GUIExceptions import ManualTaggingAbortedException

from .gui.sp_gui import SPGUIManager, Section, SectionStatus
from ..data.BBFields import BBFields

# Lets the user tag the file. Modifies MetaDataItem in place
def tag_file(file_loc, mdi:MetaDataItem):

    # Initial Tk to avoid macOS error
    t = Tk()
    t.destroy()

    while True:
        try:
            context = BBContext(
                file_loc,
                bbox_fields=mdi.bb_fields.get_fields_as_list() + [mdi.accident_locations],
                start_index=mdi.start_i,
                end_index=mdi.end_i,
                enum_tags = mdi.enum_tags
            )
            gui = BBGUIManager(context)
            gui.start()

            mdi.bb_fields.set_fields_from_list(context.get_bbox_fields()[:-1])
            mdi.accident_locations = context.get_bbox_fields()[-1]
            mdi.enum_tags = context.enum_tags

            for key, val in context.additional_tags:
                mdi.add_tag(key, val)

            if not context.is_dashcam:
                raise CancelSignal("Marked as not a dashcam video")

            return mdi

        except ManualTaggingAbortedException as e:
            print("Aborted. Will restart")

def split_file(file_loc, mdi:MetaDataItem):

    # Initial Tk to avoid macOS error
    t = Tk()
    t.destroy()

    while True:
        try:
            context = BBContext(file_loc,
                bbox_fields=mdi.bb_fields.get_fields_as_list() + [mdi.accident_locations],
                start_index=mdi.start_i,
                end_index=mdi.end_i,
                enum_tags = mdi.enum_tags
            )
            gui = SPGUIManager(context)
            rs, bbfs = gui.start()

            split_vid = len(rs) > 1 or mdi.is_split_url

            ret = []
            for i, (sec, bbf) in enumerate(zip(rs, bbfs)):
                if i == 0:
                    m = mdi
                else:
                    m = mdi.clone()

                m.start_i = sec.start
                m.end_i = sec.end
                m.enum_tags = sec.enum_tags
                m.is_split_url = split_vid
                m.is_cancelled = not (sec.status == SectionStatus.ACTIVE)

                m.bb_fields.set_fields_from_list(bbf[:-1])
                m.accident_locations = bbf[-1]

                ret.append(m)
            return ret

        except ManualTaggingAbortedException as e:
            print("Aborted. Will restart")