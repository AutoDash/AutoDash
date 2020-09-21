from .context import GUIContext
from ..utils.key_mapper import KeyMapper
from .general_gui import VideoPlayerGUIManager
from .gui_mode import InternalMode
import cv2

SP_MODE_INSTRUCTIONS = [
    ["x", "Split at the current frame exclusively", "Split is exclusive (current frame is gone)"],
    ["z", "Undo a split"],
    ["t", "Toggle the current section for deletion", "If deleted, this section will be ignored for the rest of the pipeline"],
    # ["q", "Go to previous split"], TODO later
    # ["e", "Go to next split"], TODO later
    ["r", "Undo all"],
]

class SPGUIManager(VideoPlayerGUIManager):
    WINDOW_NAME = 'splitter'

    LOG_LINES = 6
    LOG_LINE_HEIGHT = 17
    LOG_LINE_MARGIN = 2
    LOG_START_X = 250
    IMG_STARTING_Y = LOG_LINE_HEIGHT * LOG_LINES + LOG_LINE_MARGIN * (LOG_LINES + 1) + 3

    def __init__(self, context: GUIContext):
        super(SPGUIManager, self).__init__(context,
           [
               SPMode(self, context)
           ]
        )

    def start(self):
        super(SPGUIManager, self).start()

    def modify_frame(self, frame, frame_index):
        return frame

class SectionStatus(object):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"

class SPMode(InternalMode):
    def __init__(self, parent: SPGUIManager, context: GUIContext):
        super().__init__(parent, SP_MODE_INSTRUCTIONS)
        self.splits = []
        self.section_statuses = []

        self.sm = SplitManager(context.vcm.get_frames_count())

    def handle_click(self, event, x, y, flags, param):
        pass

    def handle_keyboard(self, key_mapper: KeyMapper):
        vcm = self.par.vcm
        sm = self.sm
        i = vcm.get_frame_index()

        if key_mapper.consume("r"):
            sm.reset()
        elif key_mapper.consume("x"):
            err = sm.split(i)
            if err is not None:
                self.error(err)
            else:
                self.log("New split made at {0}".format(i))
        elif key_mapper.consume("z"):
            err = sm.erase_split(i)
            if err is not None:
                self.error(err)
            else:
                self.log("Split at {0} was removed".format(i))
        elif key_mapper.consume("t"):
            err = sm.toggle_section(i)
            if err is not None:
                self.error(err)
            else:
                self.log("Current section state was toggled".format(i))

    def get_state_message(self):
        return [
            "Split Mode",
            "{0} Splits".format(self.sm.get_n_splits()),
            "{0}/{1} Deleted".format(self.sm.get_n_deleted(), self.sm.get_n_sections()),
            # "{0:.1f} % Deleted".format(), TODO later
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

class SplitManager(object):
    # Don't change anything except color
    TEXT_DISPLAY = {
        "fontFace": cv2.FONT_HERSHEY_SIMPLEX,
        "fontScale": 1,
        "color": (255, 255, 255),
        "thickness": 2
    }

    def __init__(self, frame_count):
        self.frame_count = frame_count
        self.splits = []
        self.section_statuses = [SectionStatus.ACTIVE]

    def reset(self):
        self.splits = []
        self.section_statuses = [SectionStatus.ACTIVE]

    def split(self, loc):
        info = self.__find(loc)
        if info.kind == SMLocInfo.SPLIT:
            return "Split already exists at {0}".format(loc)
        self.splits.insert(info.ii, loc)
        self.section_statuses.insert(info.ii, self.section_statuses[info.ii])

    def erase_split(self, loc):
        info = self.__find(loc)
        if info.kind != SMLocInfo.SPLIT:
            return "Frame {0} is not the location of a split".format(loc)

        ii = info.ii
        if self.section_statuses[ii] != self.section_statuses[ii+1]:
            return "Both sides of the split must be in the same state ({0} != {1})".format(
                self.section_statuses[ii], self.section_statuses[ii+1]
            )

        del self.splits[ii]
        del self.section_statuses[ii]

    def toggle_section(self, loc):
        info = self.__find(loc)
        if info.kind != SMLocInfo.SECTION:
            return "Frame {0} is a split".format(loc)
        if self.section_statuses[info.ii] == SectionStatus.ACTIVE:
            self.section_statuses[info.ii] = SectionStatus.DELETED
        else:
            self.section_statuses[info.ii] = SectionStatus.ACTIVE


    def __find(self, loc):
        ii = None
        kind = None
        if len(self.splits) == 0:
            ii = 0
            kind = SMLocInfo.SECTION
        elif loc > self.splits[-1]:
            ii = len(self.splits)
            kind = SMLocInfo.SECTION
        else:
            for i, s in enumerate(self.splits):
                if s == loc:
                    ii = i
                    kind = SMLocInfo.SPLIT
                    break
                if s > loc:
                    ii = i
                    kind = SMLocInfo.SECTION
                    break

        return SMLocInfo(loc, kind, ii)

    def modify_frame(self, frame, loc, width, height):
        def get_center(text):
            textsize = cv2.getTextSize(text,
                    self.TEXT_DISPLAY["fontFace"],
                    self.TEXT_DISPLAY["fontScale"],
                    self.TEXT_DISPLAY["thickness"])[0]
            return (width - textsize[0]) // 2
        def get_end(text):
            textsize = cv2.getTextSize(text,
                    self.TEXT_DISPLAY["fontFace"],
                    self.TEXT_DISPLAY["fontScale"],
                    self.TEXT_DISPLAY["thickness"])[0]
            return int(width - textsize[0]) - 5
        def get_start(text):
            return 5

        info = self.__find(loc)
        ii = info.ii
        kind = info.kind

        prev_text = []
        mid_text = []
        next_text = []
        if kind == SMLocInfo.SECTION:
            # Prev text
            if ii != 0:
                prev_text = ["< " + str(loc - self.splits[ii-1]), "At " + str(self.splits[ii-1])]

            # Current text
            mid_text = [self.section_statuses[ii], "Section {0}".format(ii+1)]

            # Next text
            if ii != len(self.splits):
                next_text = [str(self.splits[ii] - loc) + " >", "At " + str(self.splits[ii])]

        elif kind == SMLocInfo.SPLIT:
            # Prev text
            if ii != 0:
                prev_text = ["< " + str(loc - self.splits[ii-1]), "At " + str(self.splits[ii-1]), self.section_statuses[ii]]

            # Current text
            mid_text = ["Split {0}".format(ii+1)]

            # Next text
            if ii != len(self.splits) - 1:
                next_text = [str(self.splits[ii+1] - loc) + " >", "At " + str(self.splits[ii+1]), self.section_statuses[ii+1]]

        for i, text in enumerate(prev_text):
            cv2.putText(frame, text, (get_start(text), (i+1) * 30), **self.TEXT_DISPLAY)
        for i, text in enumerate(mid_text):
            cv2.putText(frame, text, (get_center(text), (i+1) * 30), **self.TEXT_DISPLAY)
        for i, text in enumerate(next_text):
            cv2.putText(frame, text, (get_end(text), (i+1) * 30), **self.TEXT_DISPLAY)

        return frame


    def get_n_splits(self):
        return len(self.splits)

    def get_n_deleted(self):
        return sum([x == SectionStatus.DELETED for x in self.section_statuses])

    def get_n_sections(self):
        return len(self.section_statuses)

    def get_all_active_ranges(self):
        splits = [-1] + self.splits + [self.frame_count]
        active_ranges = []
        for i in range(len(self.section_statuses)):
            if self.section_statuses[i] == SectionStatus.DELETED:
                continue
            start = splits[i]
            end = splits[i+1]

            # Start and end frames will be removed
            if not (start+1 <= end-1):
                continue

            active_ranges.append((start+1, end-1))
        return active_ranges
























