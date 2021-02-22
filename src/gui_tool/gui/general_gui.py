from src.gui_tool.utils.rotating_log import RotatingLog
from src.gui_tool.utils.key_mapper import KeyMapper
from .bb.BoundingBoxManager import BoundingBoxManager
import numpy as np
from .tinker_subuis.help_popup import HelpPopup
from .tinker_subuis.button_popup import ButtonPopup
import cv2
from ..GUIExceptions import ManualTaggingAbortedException, ManualTaggingExitedException
from .bb_context import BBContext
from .tinker_subuis.text_popup import TextPopup


class VideoPlayerGUIManager(object):
    PROGRESS_BAR_NAME = "progress"
    FRAME_RATE_BAR_NAME = "frame_delay"
    PAUSE_BUTTON_NAME = "pause"
    WINDOW_NAME = 'overwriteThis'

    LOG_LINES = 6
    LOG_LINE_HEIGHT = 17
    LOG_LINE_MARGIN = 2
    LOG_START_X = 250
    IMG_STARTING_Y = LOG_LINE_HEIGHT * LOG_LINES + LOG_LINE_MARGIN * (
        LOG_LINES + 1) + 3

    INSTRUCTIONS = [
        ["m or tab", "Switch mode"],
        ["h", "Open instructions page"],
        ["a", "1 back"],
        ["s", "10 back"],
        ["d", "1 forward"],
        ["w", "10 forward"],
        ["j", "Jump To Index"],
        ["Space", "Pause/unpause"],
        ["Enter", "Finish and continue"],
        [
            "Esc",
            "Abort and restart tagging. Will raise ManualTaggingAbortedException"
        ],
    ]

    def __init__(self, context: BBContext, mode_handlers: list):
        self.context = context
        self.vcm = self.context.vcm
        self.frame_rate = 25
        self.logger = RotatingLog(self.LOG_LINES)
        self.ignore_index_change_interval = self.vcm.get_frames_count() // 200

        self.mode_handlers = mode_handlers
        self.mode_handler_i = 0

        self.key_mapper = KeyMapper()
        self.bbm = BoundingBoxManager(self.vcm.get_frames_count())
        self.bbm.set_to(
            context,
            selected=[
                obj.id for obj in context.bbox_fields.objects.values()
                if obj.has_collision
            ],
        )

    def start(self):
        self.set_GUI()
        try:
            self.play_video()
        except ManualTaggingAbortedException:
            raise
        finally:
            self.cleanup()

    def set_GUI(self):
        cv2.namedWindow(self.WINDOW_NAME)
        cv2.resizeWindow(self.WINDOW_NAME, self.vcm.get_width(),
                         self.vcm.get_height() + self.IMG_STARTING_Y)
        cv2.setMouseCallback(
            self.WINDOW_NAME,
            lambda event, x, y, flags, param: self.handleClick(
                event, x, y, flags, param))

        def set_frame_rate_callback(value):
            self.frame_rate = max(1, value)

        def set_progress_rate_callback(value):
            if abs(value - self.vcm.get_frame_index()) > self.ignore_index_change_interval or \
                    value == 0 or value == self.vcm.get_frames_count()-1:
                self.vcm.start_from(value)

        def set_paused_callback(value):
            if self.vcm is not None:
                self.vcm.set_paused(value)

        cv2.createTrackbar(self.PROGRESS_BAR_NAME, self.WINDOW_NAME, 0,
                           max(0,
                               self.vcm.get_frames_count() - 1),
                           set_progress_rate_callback)
        cv2.createTrackbar(self.FRAME_RATE_BAR_NAME, self.WINDOW_NAME,
                           self.frame_rate, 200, set_frame_rate_callback)
        cv2.createTrackbar(self.PAUSE_BUTTON_NAME, self.WINDOW_NAME, False, 1,
                           set_paused_callback)

    def play_video(self):
        shown_for_first_time = False
        while True:
            if shown_for_first_time and cv2.getWindowProperty(
                    self.WINDOW_NAME,
                    cv2.WND_PROP_VISIBLE) <= 0:  # Window closed. Abort
                raise ManualTaggingExitedException(
                    "Tagging operation aborted by closing window")

            frame = self.vcm.next().copy()
            frame_index = self.vcm.get_frame_index()
            frame = self.modify_frame(frame, frame_index)
            frame = self.get_mode_handler().modify_frame(frame, frame_index)
            cv2.imshow(self.WINDOW_NAME, self.build_frame(frame))
            shown_for_first_time = True

            cv2.setTrackbarPos(self.PROGRESS_BAR_NAME, self.WINDOW_NAME,
                               frame_index)

            self.key_mapper.append(cv2.waitKey(self.frame_rate) & 0xFF)
            if self.key_mapper.consume("esc"):  # Escape key
                res = ButtonPopup(
                    "Confirm restart",
                    "Hitting confirm will destroy all progress. You will have to restart. Continue?",
                    ["Confirm", "Cancel"],
                ).run()
                if res == "Confirm":
                    raise ManualTaggingAbortedException(
                        "Tagging operation aborted")
            elif self.key_mapper.consume("enter"):  # Enter
                if not self.can_commit():
                    self.logger.log("[ERROR] Commit operation failed")
                else:
                    res = ButtonPopup("Confirm commit",
                                      self.get_commit_message(),
                                      ["Confirm", "Cancel"]).run()
                    if res == "Confirm":
                        break
            elif self.key_mapper.consume("h"):
                window = HelpPopup(
                    "GUI controls reference",
                    self.INSTRUCTIONS + [["", ""]] +
                    self.get_mode_handler().INSTRUCTIONS,
                )
                window.run()
            elif self.key_mapper.consume("j"):
                loc = TextPopup("Enter index to jump to, or close the window to cancel").run()
                try:
                    iloc = int(loc)
                    if iloc >= 0 and iloc <= self.vcm.get_frames_count() - 1:
                        self.vcm.start_from(iloc)
                        self.logger.log("Jumped to index {0}".format(iloc))
                    else:
                        self.logger.log("[Error]: Invalid input {0} (still on {1} of {2})".format(loc, self.vcm.get_frame_index(), self.vcm.get_frames_count()))
                except:
                        self.logger.log("[Error]: Invalid input {0} (still on {1} of {2})".format(loc, self.vcm.get_frame_index(), self.vcm.get_frames_count()))
            elif self.key_mapper.consume("a"):
                self.vcm.shift_frame_index(-1)
            elif self.key_mapper.consume("s"):
                self.vcm.shift_frame_index(-10)
            elif self.key_mapper.consume("d"):
                self.vcm.shift_frame_index(1)
            elif self.key_mapper.consume("w"):
                self.vcm.shift_frame_index(10)
            elif self.key_mapper.consume(" "):
                cv2.setTrackbarPos(self.PAUSE_BUTTON_NAME, self.WINDOW_NAME,
                                   0 if self.vcm.get_paused() else 1)

            if self.key_mapper.consume("m") or self.key_mapper.consume("tab"):
                self.mode_handler_i += 1
                self.mode_handler_i %= len(self.mode_handlers)
                self.logger.log("Changed mode")
            else:
                self.get_mode_handler().handle_keyboard(self.key_mapper)

    def build_frame(self, frame):
        img = np.zeros(
            (self.context.file_height + self.IMG_STARTING_Y,
             self.context.file_width, 3),
            np.uint8,
        )

        def write_top_text():
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_color = (255, 255, 255)
            for i, msg in enumerate(self.logger.get_logs()):
                starting_index = (self.LOG_START_X, self.LOG_LINE_HEIGHT *
                                  (i + 1) + self.LOG_LINE_MARGIN * i)
                cv2.putText(img, msg, starting_index, font, font_scale,
                            font_color)

            for i, msg in enumerate(
                    self.get_mode_handler().get_state_message()):
                starting_index = (0, self.LOG_LINE_HEIGHT * (i + 1) +
                                  self.LOG_LINE_MARGIN * i)
                cv2.putText(img, msg, starting_index, font, font_scale,
                            font_color)

        write_top_text()
        displayed = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
        img[self.IMG_STARTING_Y:, 0:] = displayed
        return img

    def handleClick(self, event, x, y, flags, param):
        y = y - self.IMG_STARTING_Y
        self.get_mode_handler().handle_click(event, x, y, flags, param)

    def get_mode_handler(self):
        return self.mode_handlers[self.mode_handler_i]

    def cleanup(self):
        self.vcm.release()
        cv2.destroyAllWindows()

    def modify_frame(self, frame, frame_index):
        raise NotImplementedError()

    def can_commit(self):
        raise NotImplementedError()

    def get_commit_message(self):
        return "Hitting confirm will commit all changes. You will not be able to undo any changes afterwards. Continue?"