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
from .gui.tinker_subuis.cashe_manager import ENUM_TAG_CACHE

def retag_if_needed(mdi: MetaDataItem):
    if mdi.is_cancelled and not ENUM_TAG_CACHE.contains_subfield(mdi.enum_tags, "Cancel"):
        mdi.enum_tags.append("CancelWithUnspecifiedReason")
    elif not mdi.is_cancelled and ENUM_TAG_CACHE.contains_subfield(mdi.enum_tags, "Cancel"):
        mdi.is_cancelled = True

# Lets the user tag the file. Modifies MetaDataItem in place
def tag_file(file_loc, mdi: MetaDataItem):

    # Initial Tk to avoid macOS error
    t = Tk()
    t.destroy()

    while True:
        try:
            retag_if_needed(mdi)
            context = BBContext(
                file_loc,
                bbox_fields=mdi.bb_fields.clone(),
                start_index=mdi.start_i,
                end_index=mdi.end_i,
                enum_tags=mdi.enum_tags,
            )
            gui = BBGUIManager(context)
            gui.start()

            mdi.bb_fields = context.get_bbox_fields()
            mdi.enum_tags = context.enum_tags.copy()

            for key, val in context.additional_tags:
                mdi.add_tag(key, val)

            if ENUM_TAG_CACHE.contains_subfield(mdi.enum_tags, "Cancel"):
                raise CancelSignal("Video was canceled via a tag")

            return mdi

        except ManualTaggingAbortedException:
            print("Aborted. Will restart")


def split_file(file_loc, mdi: MetaDataItem):

    # Initial Tk to avoid macOS error
    t = Tk()
    t.destroy()

    while True:
        try:
            retag_if_needed(mdi)
            context = BBContext(
                file_loc,
                bbox_fields=mdi.bb_fields.clone(),
                start_index=mdi.start_i,
                end_index=mdi.end_i,
                enum_tags=mdi.enum_tags,
            )
            gui = SPGUIManager(context)
            rs, bbfs = gui.start()
            print(f"split done, rs: {rs}")

            split_vid = len(rs) > 1 or mdi.is_split_url

            ret = []
            for i, (sec, bbf) in enumerate(zip(rs, bbfs)):
                if i == 0:
                    m = mdi
                else:
                    m = mdi.clone()

                m.start_i = sec.start
                m.end_i = sec.end
                m.enum_tags = sec.enum_tags.copy()
                m.is_split_url = split_vid
                m.is_cancelled = ENUM_TAG_CACHE.contains_subfield(m.enum_tags, "Cancel")

                m.bb_fields = bbf

                ret.append(m)
            return ret

        except ManualTaggingAbortedException as e:
            print("Aborted. Will restart")