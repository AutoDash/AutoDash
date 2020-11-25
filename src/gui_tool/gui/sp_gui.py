from __future__ import annotations
from .bb_context import BBContext
from ..utils.key_mapper import KeyMapper
from .general_gui import VideoPlayerGUIManager
from .gui_mode import InternalMode
import cv2
from .tinker_subuis.multiselect_popup import MultiSelectPopup
from typing import List
from .bb.BoundingBoxManager import BoundingBoxManager
from .tinker_subuis.button_popup import ButtonPopup

SP_MODE_INSTRUCTIONS = [
    ["x", "Split at the current frame exclusively", "Split is exclusive (current frame is gone)"],
    ["z", "Undo a split"],
    ["t", "Toggle the current section for deletion", "If deleted, this section will be ignored for the rest of the pipeline"],
    ["q", "Jump to previous split"],
    ["e", "Jump to next split"],
    ["v", "Set enum tags for the CURRENT section"],
    ["r*2", "reset enum tags the CURRENT section"],
    ["o*2", "Remove all bounding boxes in this video", "Applies to whole video, not just the current section"],
]

DEBUG_MODE = False

class SPGUIManager(VideoPlayerGUIManager):
    WINDOW_NAME = 'splitter'

    LOG_LINES = 6
    LOG_LINE_HEIGHT = 17
    LOG_LINE_MARGIN = 2
    LOG_START_X = 250
    IMG_STARTING_Y = LOG_LINE_HEIGHT * LOG_LINES + LOG_LINE_MARGIN * (LOG_LINES + 1) + 3

    def __init__(self, context: BBContext):
        super(SPGUIManager, self).__init__(context,
           [
               SPMode(self, context)
           ]
        )

    def get_return_fields(self) -> (List[Section], List[List]):
        sections = self.mode_handlers[0].sm.get_all_sections()
        bbfs = []
        for sec in sections:
            bbfs.append(self.bbm.extract_in_range(
                sec.start,
                sec.end
            ))
        if self.context.start_index is not None and self.context.start_index > 0:
            for sec in sections:
                sec.start += self.context.start_index
                sec.end += self.context.start_index
        return sections, bbfs

    def start(self) -> (List[Section], List[List]):
        super(SPGUIManager, self).start()
        return self.get_return_fields()

    def verify_bounding_box_consistency(self):
        sections, bbfs = self.get_return_fields()
        success = True
        for i, b in enumerate(bbfs):
            selected = b[-2]
            accident_locs = b[-1]
            if len(accident_locs) == 0 and len(selected) > 0:
                self.logger.log("[WARN]: Section {0} has accident location despite no marked participants".format(i+1))
                success = False
            if len(accident_locs) > 0 and len(selected) == 0:
                self.logger.log("[WARN]: Section {0} contains marked accident participants, but no accident location".format(i+1))
                success = False
        return success

    def modify_frame(self, frame, frame_index):
        frame = self.bbm.modify_frame(frame, frame_index)
        return frame

    def can_commit(self):
        return True

    def get_commit_message(self):
        if not self.verify_bounding_box_consistency():
            return "\n".join([
                "WARNING:",
                "There are warnings related to accident locations.",
                "You cannot fix them in this GUI tool without clearing all bonding boxes.",
                "Hitting continue will ignore this problem",
                "Do you wish to continue?"
            ])
        return super(SPGUIManager, self).get_commit_message()

class SectionStatus(object):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"

class SPMode(InternalMode):
    def __init__(self, parent: SPGUIManager, context: BBContext):
        super().__init__(parent, SP_MODE_INSTRUCTIONS)
        self.splits = []
        self.section_statuses = []

        self.sm = SplitManager(self, context.vcm.get_frames_count(), context.enum_tags.copy())

    def handle_click(self, event, x, y, flags, param):
        pass

    def handle_keyboard(self, key_mapper: KeyMapper):
        vcm = self.par.vcm
        sm = self.sm
        i = vcm.get_frame_index()

        if key_mapper.consume("x"):
            sm.split(i)
        elif key_mapper.consume("z"):
            sm.erase_split(i)
        elif key_mapper.consume("t"):
            sm.toggle_section(i)
        elif key_mapper.consume("q"):
            p_loc = sm.find_previous_split_location(i)
            if p_loc is not None:
                self.par.vcm.start_from(p_loc)
            else:
                self.error("Can't jump: No previous split exists")
        elif key_mapper.consume("e"):
            n_loc = sm.find_next_split_location(i)
            if n_loc is not None:
                self.par.vcm.start_from(n_loc)
            else:
                self.error("Can't jump: No next split exists")
        elif key_mapper.consume("v"):
            curr_tags = sm.get_enum_tags_at(i)
            if curr_tags is None:
                self.error("Cannot set tags on a split")
            else:
                window = MultiSelectPopup("Select custom enum tags", "video_enum_tags", curr_tags)
                enum_tags = window.run()
                if enum_tags is not None:
                    self.log("Updated from {0}".format(curr_tags))
                    self.log("Now: {0}".format(enum_tags))
                    self.sm.set_enum_tags_at(i, enum_tags)
                    self.log("Remember to commit any new tags!")
                else:
                    self.log("Enum tag update cancelled")
        elif key_mapper.consume(("r", "r")):
            curr_tags = sm.get_enum_tags_at(i)
            if curr_tags is None:
                self.error("Cannot reset tags on a split")
            else:
                self.sm.set_enum_tags_at(i, [])
                self.log("Removing all enum tags (previously {0})".format(curr_tags))
        elif key_mapper.consume(("o", "o")):
            res = ButtonPopup(
                "Confirm clearing ALL bounding boxes",
                "Are you sure you want to clear ALL bounding boxes, across ALL sections of this video?",
                ["Confirm", "Cancel"]
            ).run()
            if res == "Confirm":
                self.par.bbm = BoundingBoxManager(self.par.bbm.total_frames)
                self.log("All bounding boxes removed")

    def get_state_message(self):
        return [
            "Split Mode",
            "{0}/{1} Deleted".format(self.sm.get_n_deleted(), self.sm.get_n_sections()),
            "{0:.1f}% Deleted".format(self.sm.get_prop_deleted() * 100.0),
            "{0} Uq. Tag sets".format(self.sm.get_n_unique_tag_sets()),
            "{0} Total tags".format(self.sm.get_n_total_tags()),
        ]

    def modify_frame(self, frame, i):
        frame = self.sm.modify_frame(frame, i, self.par.vcm.get_width(), self.par.vcm.get_height())
        return frame

class SMLocInfo(object):
    SPLIT = "SPLIT"
    SECTION = "SECTION"
    def __init__(self, loc: int, kind: str, ii: int):
        self.loc = loc
        self.kind = kind
        self.ii = ii

class DisplayParams(object):
    def __init__(self, text, line_num, x_loc, formatter):
        self.text = text
        self.line_num = line_num
        self.x_loc = x_loc
        self.formatter = formatter

class Section(object):
    def __init__(self, start: int, end: int, status: str, enum_tags: List[str]):
        self.start = start
        self.end = end
        self.status = status
        self.enum_tags = enum_tags

    def split_failure_msg(self, loc):
        if abs(loc-self.start)<=0:
            return "Split location too close to a previous split at {0}".format(self.start-1)
        if abs(loc-self.end)<=1:
            return "Split location too close to next split ar {0}".format(self.end)
        return None

    def split(self, loc) -> (Section, Section):
        s1 = Section(self.start, loc, self.status, self.enum_tags.copy())
        s2 = Section(loc+1, self.end, self.status, self.enum_tags.copy())
        return s1, s2

    @classmethod
    def join_failure_msg(cls, s1: Section, s2: Section):
        if s1.enum_tags != s2.enum_tags:
            return "The enum tags of the 2 sections are not equal"
        if s1.status != s2.status:
            return "The status of the 2 sections are not equal"
        if s1.start > s2.start:
            s1, s2 = s2, s1
        if s1.end + 1 != s2.start:
            return "Internal error. 2 sections are not connected"
        return None

    @classmethod
    def join(cls, s1: Section, s2: Section) -> Section:
        return Section(min(s1.start, s2.start), max(s1.end, s2.end), s1.status, s1.enum_tags.copy())

    def toggle_status(self):
        if self.status == SectionStatus.ACTIVE:
            self.status = SectionStatus.DELETED
        else:
            self.status = SectionStatus.ACTIVE

class SplitManager(object):
    # Color in BGR
    SPLIT_DISPLAY =   {"fontFace": cv2.FONT_HERSHEY_SIMPLEX, "fontScale": 1, "thickness": 2, "color": (153, 51, 51)}
    DELETED_DISPLAY = {"fontFace": cv2.FONT_HERSHEY_SIMPLEX, "fontScale": 1, "thickness": 2, "color": (10, 10, 204)}
    ACTIVE_DISPLAY =  {"fontFace": cv2.FONT_HERSHEY_SIMPLEX, "fontScale": 1, "thickness": 2, "color": (51, 204, 51)}
    ENUM_DISPLAY =    {"fontFace": cv2.FONT_HERSHEY_SIMPLEX, "fontScale": 0.5, "thickness": 1, "color": (150, 150, 150)}
    CURRENT_LOC_COLOR = (51, 153, 255)

    def __init__(self, parent: SPMode, frame_count: int, initial_enum_tags: List[str]):
        self.par = parent
        self.frame_count = frame_count
        if initial_enum_tags is None:
            initial_enum_tags = []
        self.secs = [Section(0, self.frame_count, SectionStatus.ACTIVE, initial_enum_tags)]

    def split(self, loc):
        if loc == 0 or loc == self.frame_count - 1:
            return self.par.error("Cannot split at endpoints")

        info = self.__find(loc)
        if info.kind == SMLocInfo.SPLIT:
            return self.par.error("Split already exists at {0}".format(loc))

        ii = info.ii
        if self.secs[ii].status == SectionStatus.DELETED:
            self.par.warn("Splitting on a deleted section. Both sides will be deleted")

        fail_msg = self.secs[ii].split_failure_msg(loc)
        if fail_msg is not None:
            return self.par.error("Splitting failed: {0}".format(fail_msg))

        s1, s2 = self.secs[info.ii].split(loc)
        self.secs[ii] = s1
        self.secs.insert(ii+1, s2)
        self.par.log("New split made at {0}".format(loc))

    def erase_split(self, loc):
        if loc == 0 or loc == self.frame_count - 1:
            return self.par.error("Nothing to join at video endpoints")

        info = self.__find(loc)
        if info.kind != SMLocInfo.SPLIT:
            return self.par.error("Frame {0} is not the location of a split".format(loc))
        ii = info.ii

        fail_msg = Section.join_failure_msg(self.secs[ii], self.secs[ii+1])
        if fail_msg is not None:
            return self.par.error("Joining failed: {0}".format(fail_msg))

        s = Section.join(self.secs[ii], self.secs[ii+1])
        self.secs[ii] = s
        del self.secs[ii+1]
        self.par.log("Split at {0} was removed".format(loc))

    def toggle_section(self, loc):
        info = self.__find(loc)
        if loc != 0 and info.kind != SMLocInfo.SECTION:
            return self.par.error("Frame {0} is a split".format(loc))
        self.secs[info.ii].toggle_status()
        self.par.log("Current section state was toggled to {0}".format(self.secs[info.ii].status))

    def __find(self, loc) -> SMLocInfo:
        ii = None
        kind = None
        if loc == 0:
            return SMLocInfo(loc, SMLocInfo.SPLIT, 0)
        for i, s in enumerate(self.secs):
            if s.end == loc:
                ii = i
                kind = SMLocInfo.SPLIT
                break
            if s.start <= loc < s.end:
                ii = i
                kind = SMLocInfo.SECTION
                break

        return SMLocInfo(loc, kind, ii)

    def find_previous_split_location(self, loc) -> int:
        for sec in reversed(self.secs):
            if sec.end < loc:
                return sec.end
        return None

    def find_next_split_location(self, loc) -> int:
        for sec in self.secs[:-1]:
            if sec.end > loc:
                return sec.end
        return None

    def modify_frame(self, frame, loc, width, height):
        def get_location(text, center_pct, formatter):
            textsize = cv2.getTextSize(text,
                    formatter["fontFace"],
                    formatter["fontScale"],
                    formatter["thickness"])[0]
            target_loc = (width - 10) * center_pct + 5
            return max(
                min(
                    int(target_loc - (textsize[0] // 2)),
                    width - 5 - textsize[0]
                ),
                5
            )

        def f_by_status(status):
            return self.DELETED_DISPLAY if status == SectionStatus.DELETED else self.ACTIVE_DISPLAY

        def build_minimap():
            if self.frame_count == 1:
                return
            ratio = (width-20.0)/(self.frame_count-1)
            def t(val):
                return max(10, min(width-10, int(val*ratio) + 10))
            current_x = t(loc)
            for sec in self.secs:
                color = f_by_status(sec.status)["color"]
                cv2.rectangle(frame, (t(sec.start-1), 10), (t(sec.end), 20), color, thickness=-1)
            on_split = loc == 0
            for sec in self.secs[:-1]:
                mark_loc = t(sec.end)
                cv2.rectangle(frame, (mark_loc-1, 8), (mark_loc+1, 22), self.SPLIT_DISPLAY["color"], thickness=-1)
                if mark_loc == current_x:  # Having current ontop of split when it is not a split is misleading
                    if sec.end>loc:
                        current_x -= 1
                    elif sec.end < loc:
                        current_x += 1
                    else:
                        on_split = True
            cv2.rectangle(frame, (current_x-1, 5), (current_x+1, 25), self.CURRENT_LOC_COLOR, thickness=-1)
            if on_split:
                cv2.rectangle(frame, (current_x, 5), (current_x, 25), self.SPLIT_DISPLAY["color"], thickness=-1)

        build_minimap()

        info = self.__find(loc)
        ii = info.ii
        kind = info.kind

        to_display = []
        if loc == 0 or kind == SMLocInfo.SECTION:
            # Prev text
            sec = self.secs[ii]
            if ii != 0:
                to_display.append(DisplayParams("< " + str(loc - sec.start+1),
                                                0, 0.0, self.SPLIT_DISPLAY))
                to_display.append(DisplayParams("At " + str(sec.start+1),
                                                1, 0.0, self.SPLIT_DISPLAY))


            # Current text
            to_display.append(DisplayParams("Section {0}".format(ii+1),
                                            0, 0.5, f_by_status(self.secs[ii].status)))
            to_display.append(DisplayParams(str(self.secs[ii].enum_tags),
                                            1, 0.5, self.ENUM_DISPLAY))


            # Next text
            if ii <= len(self.secs)-2:
                to_display.append(DisplayParams(str(sec.end - loc) + " >",
                                                0, 1.0, self.SPLIT_DISPLAY))
                to_display.append(DisplayParams("At " + str(sec.end),
                                                1, 1.0, self.SPLIT_DISPLAY))

        elif kind == SMLocInfo.SPLIT:
            # Prev text
            if ii >= 1:
                to_display.append(DisplayParams("< " + str(loc - self.secs[ii-1].end),
                                                0, 0.0, self.SPLIT_DISPLAY))
                to_display.append(DisplayParams( "At " + str(self.secs[ii-1].end),
                                                1, 0.0, self.SPLIT_DISPLAY))

            # Current text
            to_display.append(DisplayParams("Split {0}".format(ii),
                                            0, 0.5, self.SPLIT_DISPLAY))

            # Next text
            if ii <= len(self.secs) - 3:
                to_display.append(DisplayParams(str(self.secs[ii+1].end - loc) + " >",
                                                0, 1.0, self.SPLIT_DISPLAY))
                to_display.append(DisplayParams("At " + str(self.secs[ii+1].end),
                                                1, 1.0, self.SPLIT_DISPLAY))

        for p in to_display:
            if len(p.text) > 70:
                p.text = p.text[:67] + "..."
            cv2.putText(frame, p.text, (get_location(p.text, p.x_loc, p.formatter), (p.line_num+1) * 30 + 25), **p.formatter)

        if DEBUG_MODE:
            self.validate()
        return frame


    def get_n_sections(self):
        return len(self.secs)

    def get_n_deleted(self):
        return sum([x.status == SectionStatus.DELETED for x in self.secs])

    def get_all_sections(self) -> List[Section]:
        return self.secs

    def get_prop_deleted(self):
        deleted_frames = len(self.secs)-1 # Endpoints are gone
        for sec in self.secs:
            if sec.status == SectionStatus.DELETED:
                deleted_frames += sec.end - sec.start

        return deleted_frames * 1.0 / self.frame_count

    # Check consistency
    def validate(self):
        for s1, s2 in zip(self.secs[:-1], self.secs[1:]):
            if s1.end + 1 != s2.start:
                raise ValueError("Connection check failed")

        if self.secs[0].start != 0:
            raise ValueError("Start changed")

        if self.secs[-1].end != self.frame_count:
            raise ValueError("End changed")

        for sec in self.secs:
            if not (sec.start < sec.end):
                raise ValueError("Invalid section start and end locations")

        if sum([sec.end-sec.start+1 for sec in self.secs]) != self.frame_count+1:
            raise ValueError("Total number of frames is not correct")

        if len(set([id(sec.enum_tags) for sec in self.secs])) != len(self.secs):
            raise ValueError("Two sections are using the same enum tag array")

    def get_enum_tags_at(self, loc) -> List[str]:
        info = self.__find(loc)
        if loc != 0 and info.kind == SMLocInfo.SPLIT:
            return None
        return self.secs[info.ii].enum_tags.copy()

    def set_enum_tags_at(self, loc, enum_tags):
        info = self.__find(loc)
        if loc != 0 and info.kind == SMLocInfo.SPLIT:
            return
        self.secs[info.ii].enum_tags = enum_tags.copy()

    def get_n_unique_tag_sets(self) -> int:
        ret = []
        for sec in self.secs:
            ret.append(tuple(sec.enum_tags))
        return len(set(ret))


    def get_n_total_tags(self) -> int:
        ret = set()
        for sec in self.secs:
            for tag in sec.enum_tags:
                ret.add(tag)
        return len(ret)

    # Hotfix
    def get_all_used_tags(self):
        ret = []
        for sec in self.secs:
            for tag in sec.enum_tags:
                if tag not in ret:
                    ret.append(tag)
        return ret













