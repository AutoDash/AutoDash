from src.gui_tool.utils import get_ord, RotatingLog
import numpy as np
import cv2
from .VideoTaggingContext import VideoTaggingContext
from .BoundingBoxManager import BoundingBoxManager
from .additional_tags import AdditionalTagWindow
from enum import Enum, auto

class ManualTaggingAbortedException(Exception):
    '''Raise when user aborts the tagging'''

class GUIModes(Enum):
    SELECTION = auto()
    BBOX = auto()

class VideoPlayerGUIManager(object):
    PROGRESS_BAR_NAME = "progress"
    FRAME_RATE_BAR_NAME = "frame_delay"
    PAUSE_BUTTON_NAME = "pause"
    WINDOW_NAME = 'tagger'

    LOG_LINES = 1
    LOG_LINE_HEIGHT = 17
    LOG_LINE_MARGIN = 2
    IMG_STARTING_Y = LOG_LINE_HEIGHT * LOG_LINES + LOG_LINE_MARGIN * (LOG_LINES + 1) + 3

    def __init__(self, context: VideoTaggingContext):
        self.context = context
        self.vcm = self.context.vcm
        self.frame_rate = 25
        self.result = self.context.result
        self.logger = RotatingLog(self.LOG_LINES)
        self.bbm = BoundingBoxManager(
            frames=["1"],
            ids=["test"],
            clss=["testCls"],
            x1s=[50],
            y1s=[50],
            x2s=[100],
            y2s=[100],
        )

        self.selection_mode_handler = InternaSelectionMode(self)
        self.mode_handler = self.selection_mode_handler

    def start(self):
        self.set_GUI()
        try:
            self.logger.log("Starting with: " + str(self.result))
            self.play_video()
        except ManualTaggingAbortedException:
            raise
        finally:
            self.cleanup()

    def set_GUI(self):
        cv2.namedWindow(self.WINDOW_NAME)
        cv2.setMouseCallback(self.WINDOW_NAME,
             lambda event, x, y, flags, param: self.handleClick(event, x, y, flags, param))

        def set_frame_rate_callback(value):
            self.frame_rate = max(1, value)
        def set_progress_rate_callback(value):
            if abs(value - self.vcm.get_frame_index()) < 5:
                return
            self.vcm.start_from(value)
        def set_paused_callback(value):
            if self.vcm is not None:
                self.vcm.set_paused(value)

        cv2.createTrackbar(self.PROGRESS_BAR_NAME, self.WINDOW_NAME, 0, max(0, self.vcm.get_frames_count()),
                           set_progress_rate_callback)
        cv2.createTrackbar(self.FRAME_RATE_BAR_NAME, self.WINDOW_NAME,
                           self.frame_rate, 60, set_frame_rate_callback)
        cv2.createTrackbar(self.PAUSE_BUTTON_NAME,  self.WINDOW_NAME,
                           False, 1, set_paused_callback)

    def play_video(self):
        while True:
            frame = self.vcm.next()
            frame = self.bbm.modify_frame(frame, self.vcm.get_frame_index())
            cv2.imshow(self.WINDOW_NAME, self.build_frame(frame))

            cv2.setTrackbarPos(self.PROGRESS_BAR_NAME, self.WINDOW_NAME, self.vcm.get_frame_index())

            received_key = cv2.waitKey(self.frame_rate) & 0xFF
            if received_key == get_ord("esc"):  # Escape key
                raise ManualTaggingAbortedException("Tagging operation aborted")
            elif received_key == get_ord("enter"):  # Enter
                break
            elif received_key == ord("t"):
                window = AdditionalTagWindow()
                tags = window.get_user_tags()
                self.result.set_additional_tags(tags)
            self.mode_handler.handle_keyboard(received_key)

    def build_frame(self, frame):
        img = np.zeros((
            self.context.file_height + self.IMG_STARTING_Y,
            self.context.file_width,
            3), np.uint8)

        def write_top_text():
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_color = (255, 255, 255)
            for i, msg in enumerate(self.logger.get_logs()):
                starting_index = (0, self.LOG_LINE_HEIGHT * (i+1) + self.LOG_LINE_MARGIN * i)
                cv2.putText(img, msg, starting_index,
                            font, font_scale, font_color)

        write_top_text()
        displayed = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
        img[self.IMG_STARTING_Y:, 0:] = displayed
        return img

    def handleClick(self, event, x, y, flags, param):
        y = y-self.IMG_STARTING_Y
        self.mode_handler.handle_click(event, x, y, flags, param)

    def cleanup(self):
        self.vcm.release()
        cv2.destroyAllWindows()

class InternalMode(object):
    def __init__(self, parent: VideoPlayerGUIManager):
        self.par = parent
    def handle_click(self, event, x, y, flags, param):
        raise NotImplementedError()
    def handle_keyboard(self, received_key: int):
        raise NotImplementedError()

class InternaSelectionMode(InternalMode):
    def handle_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.par.bbm.handleClickSelection(self.par.vcm.get_frame_index(), x, y)
    def handle_keyboard(self, received_key: int):
        par = self.par
        mark_changed = False
        if received_key == get_ord("a"):
            par.vcm.shift_frame_index(-1)
        elif received_key == get_ord("s"):
            par.vcm.shift_frame_index(-10)
        elif received_key == get_ord("d"):
            par.vcm.shift_frame_index(1)
        elif received_key == get_ord("w"):
            par.vcm.shift_frame_index(10)
        elif received_key == get_ord(" "):
            cv2.setTrackbarPos(par.PAUSE_BUTTON_NAME, par.WINDOW_NAME, 0 if par.vcm.get_paused() else 1)
        elif received_key == get_ord("u"):
            par.result.unmark()
            mark_changed = True
        elif received_key == get_ord("n"):
            par.result.mark_is_dashcam(not par.result.is_dashcam)
            mark_changed = True
        elif received_key == get_ord("m"):
            par.result.mark_accident(par.vcm.get_frame_index())
            mark_changed = True
        elif received_key == get_ord(","):  # , Key
            par.result.unmark_last()
            mark_changed = True
        if mark_changed:
            par.logger.log(str(par.result))