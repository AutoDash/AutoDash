from src.gui_tool.utils import RotatingLog, KeyMapper
import numpy as np
from .VideoTaggingContext import VideoTaggingContext
from .BoundingBoxManager import BoundingBoxManager
from .tinker_subuis.additional_tags import AdditionalTagWindow
from .tinker_subuis.text_popup import PopUpWindow
from .tinker_subuis.help_popup import HelpPopup
from .tinker_subuis.button_popup import ButtonPopup
import cv2
from .GUIExceptions import ManualTaggingAbortedException, ManualTaggingExitedException
from .BoundingBoxInputManager import IndexedRectBuilder, BoundingBoxInputManager

GENERAL_INSTRUCTIONS = [
    ["m", "Switch mode"],
    ["h", "Open instructions page"],
    ["a", "1 back"],
    ["s", "10 back"],
    ["d", "1 forward"],
    ["w", "10 forward"],
    ["Space", "Pause/unpause"],
    ["Enter * 2", "Finish and continue"],
    ["Esc * 2", "Abort and restart tagging. Will raise ManualTaggingAbortedException"],
]
BBOX_MODE_INSTRUCTIONS = [
    ["click & drag", "Create bounding box range for commands"],
    ["r", "Reset current task"],
    ["q", "Select the previous existing bounding box for this object id as input"],
    ["e", "Select the next existing bounding box for this object id as input"],
    ["z", "Undo click and drag action (Remove drawn box from input)"],
    ["x", "Change frame index of the last bounding box input to the current frame"],
    ["p", "Remove all unused bounding box ids (ids without any bounding boxes)"],
    # ["gf", "Re-interpolate over all frames.",
    #       "Will not reinterpolate to the beginning or end of video"],
    # ["gg", "Re-interpolate here through current empty frame",
    #       "will not reinterpolate to the beginning or end of video"],

    ["b", "If only 1 bounding box input drawn, defines single bounding box",
          "If only 2 bounding box inputs drawn, defines bounding boxes over range"],
    ["c", "Clear existing bounding boxes over frames", "Press after clicking on 2 frames"],
    ["v", "Clear a single bounding box on this frame only" "Does not require inputs"],

    ["i", "Select a new integer ID to work on", "If ID already exists, will select original"],
    ["u", "Select a class for the current object id", "This will overwrite the original"],
]
SELECTION_MODE_INSTRUCTIONS = [
    ["mouse click", "Select bounding box"],
    ["n",
        "Toggle whether it is a dashcam video",
        "NOTE: by default, all videos will be dashcam",
        "Pressing n the first time will mark the video as not dashcam"],
    ["t", "Opens window for user customizable tags"],
]

class VideoPlayerGUIManager(object):
    PROGRESS_BAR_NAME = "progress"
    FRAME_RATE_BAR_NAME = "frame_delay"
    PAUSE_BUTTON_NAME = "pause"
    WINDOW_NAME = 'tagger'

    LOG_LINES = 6
    LOG_LINE_HEIGHT = 17
    LOG_LINE_MARGIN = 2
    LOG_START_X = 250
    IMG_STARTING_Y = LOG_LINE_HEIGHT * LOG_LINES + LOG_LINE_MARGIN * (LOG_LINES + 1) + 3

    def __init__(self, context: VideoTaggingContext):
        self.context = context
        self.vcm = self.context.vcm
        self.frame_rate = 25
        self.logger = RotatingLog(self.LOG_LINES)
        self.ignore_index_change_interval = self.vcm.get_frames_count() // 200

        self.bbm = BoundingBoxManager(self.vcm.get_frames_count())
        self.bbm.set_to(*context.get_bbox_fields_as_list())

        self.mode_handlers = [
            InternaSelectionMode(self),
            InternalBBoxMode(self)
        ]
        self.mode_handler_i = 0

        self.instructions = GENERAL_INSTRUCTIONS
        self.key_mapper = KeyMapper()

    def start(self):
        self.set_GUI()
        try:
            self.logger.log("Starting with: {0} bounding box ids".format(self.bbm.get_n_ids()))
            self.play_video()
        except ManualTaggingAbortedException:
            raise
        finally:
            self.cleanup()

        self.context.set_bbox_fields_from_list(self.bbm.extract())

    def set_GUI(self):
        cv2.namedWindow(self.WINDOW_NAME)
        cv2.setMouseCallback(self.WINDOW_NAME,
             lambda event, x, y, flags, param: self.handleClick(event, x, y, flags, param))

        def set_frame_rate_callback(value):
            self.frame_rate = max(1, value)
        def set_progress_rate_callback(value):
            if abs(value - self.vcm.get_frame_index()) > self.ignore_index_change_interval or \
                    value == 0 or value == self.vcm.get_frames_count()-1:
                self.vcm.start_from(value)
        def set_paused_callback(value):
            if self.vcm is not None:
                self.vcm.set_paused(value)

        cv2.createTrackbar(self.PROGRESS_BAR_NAME, self.WINDOW_NAME, 0, max(0, self.vcm.get_frames_count()-1),
                           set_progress_rate_callback)
        cv2.createTrackbar(self.FRAME_RATE_BAR_NAME, self.WINDOW_NAME,
                           self.frame_rate, 200, set_frame_rate_callback)
        cv2.createTrackbar(self.PAUSE_BUTTON_NAME,  self.WINDOW_NAME,
                           False, 1, set_paused_callback)

    def play_video(self):
        shown_for_first_time = False
        while True:
            if shown_for_first_time and cv2.getWindowProperty(self.WINDOW_NAME, cv2.WND_PROP_VISIBLE) <= 0:  # Window closed. Abort
                raise ManualTaggingExitedException("Tagging operation aborted by closing window")

            frame = self.vcm.next().copy()
            frame_index = self.vcm.get_frame_index()
            frame = self.bbm.modify_frame(frame, frame_index)
            frame = self.get_mode_handler().modify_frame(frame, frame_index)
            cv2.imshow(self.WINDOW_NAME, self.build_frame(frame))
            shown_for_first_time = True

            cv2.setTrackbarPos(self.PROGRESS_BAR_NAME, self.WINDOW_NAME, frame_index)

            self.key_mapper.append(cv2.waitKey(self.frame_rate) & 0xFF)
            if self.key_mapper.consume(("esc", "esc")):  # Escape key
                res = ButtonPopup(
                    "Confirm restart",
                    "Hitting confirm will destroy all progress. You will have to restart. Continue?",
                    ["Confirm", "Cancel"]
                ).run()
                if res == "Confirm":
                    raise ManualTaggingAbortedException("Tagging operation aborted")
            elif self.key_mapper.consume(("enter", "enter")):  # Enter
                res = ButtonPopup(
                    "Confirm commit",
                    "Hitting confirm will commit all changes. You will not be able to undo any changes afterwards. Continue?",
                    ["Confirm", "Cancel"]
                ).run()
                if res == "Confirm":
                    break
            elif self.key_mapper.consume("h"):
                window = HelpPopup(
                    "GUI controls reference",
                    self.instructions + [["", ""]] + self.get_mode_handler().instructions
                )
                window.run()
            elif self.key_mapper.consume("a"):
                self.vcm.shift_frame_index(-1)
            elif self.key_mapper.consume("s"):
                self.vcm.shift_frame_index(-10)
            elif self.key_mapper.consume("d"):
                self.vcm.shift_frame_index(1)
            elif self.key_mapper.consume("w"):
                self.vcm.shift_frame_index(10)
            elif self.key_mapper.consume(" "):
                cv2.setTrackbarPos(self.PAUSE_BUTTON_NAME, self.WINDOW_NAME, 0 if self.vcm.get_paused() else 1)

            if self.key_mapper.consume("m"):
                self.mode_handler_i += 1
                self.mode_handler_i %= len(self.mode_handlers)
                self.logger.log("Changed mode")
            else:
                self.get_mode_handler().handle_keyboard(self.key_mapper)

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
                starting_index = (self.LOG_START_X, self.LOG_LINE_HEIGHT * (i+1) + self.LOG_LINE_MARGIN * i)
                cv2.putText(img, msg, starting_index,
                            font, font_scale, font_color)

            for i, msg in enumerate(self.get_mode_handler().get_state_message()):
                starting_index = (0, self.LOG_LINE_HEIGHT * (i + 1) + self.LOG_LINE_MARGIN * i)
                cv2.putText(img, msg, starting_index,
                            font, font_scale, font_color)

        write_top_text()
        displayed = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
        img[self.IMG_STARTING_Y:, 0:] = displayed
        return img

    def handleClick(self, event, x, y, flags, param):
        y = y-self.IMG_STARTING_Y
        self.get_mode_handler().handle_click(event, x, y, flags, param)

    def get_mode_handler(self):
        return self.mode_handlers[self.mode_handler_i]

    def cleanup(self):
        self.vcm.release()
        cv2.destroyAllWindows()

class InternalMode(object):
    def __init__(self, parent: VideoPlayerGUIManager, instructions: list):
        self.par = parent
        self.instructions = instructions
    def handle_click(self, event, x, y, flags, param):
        raise NotImplementedError()
    def handle_keyboard(self, key_mapper: KeyMapper):
        raise NotImplementedError()
    def get_state_message(self):
        raise NotImplementedError()
    def modify_frame(self, frame, i):
        return frame
    def log(self, msg):
        self.par.logger.log(msg)
    def hint(self, msg):
        self.log("[HINT] {0}".format(msg))
    def error(self, msg):
        self.log("[ERROR] {0}".format(msg))
    def warn(self, msg):
        self.log("[WARN] {0}".format(msg))
    def cancel(self, op, msg):
        self.log("[CANCELLED: {0}] {1}".format(op, msg))

class InternaSelectionMode(InternalMode):
    def __init__(self, parent: VideoPlayerGUIManager):
        super().__init__(parent, SELECTION_MODE_INSTRUCTIONS)
    def handle_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            modified_id = self.par.bbm.handleClickSelection(self.par.vcm.get_frame_index(), x, y)
            if modified_id is not None:
                self.log("Set object {0} as {1}".format(
                    modified_id,
                    "part of collision" if self.par.bbm.get_is_selected(modified_id) else "not part of collision"
                ))
    def handle_keyboard(self, key_mapper: KeyMapper):
        par = self.par
        if key_mapper.consume("n"):
            par.context.mark_is_dashcam(not par.context.is_dashcam)
            self.log("Marked video as {0}".format("dashcam" if par.context.is_dashcam else "not dashcam"))
        elif key_mapper.consume("t"):
            window = AdditionalTagWindow()
            tags = window.get_user_tags()
            par.context.set_additional_tags(tags)
            self.log("Additional tags set")
    def get_state_message(self):
        return [
            "Selection Mode",
            "{0} Selected".format(self.par.bbm.get_n_selected()),
            "{0} Total".format(self.par.bbm.get_n_ids()),
            "Is dashcam" if self.par.context.is_dashcam else "Not dashcam"
        ]

class InternalBBoxMode(InternalMode):
    BOX_DRAWING_DISPLAY = {
        "color": (150, 255, 150),
        "lineType": 2,
        "thickness": 2
    }
    DEFAULT_CLASS = "NONE"

    def __init__(self, parent: VideoPlayerGUIManager):
        super().__init__(parent, BBOX_MODE_INSTRUCTIONS)
        self.mouse_position = None
        self.im = BoundingBoxInputManager()
        self.irb = IndexedRectBuilder()
        self.selected_id = 1

    def handle_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.irb.set_initial_point(x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            self.mouse_position = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            if self.irb.has_initial_point():
                ir = self.irb.to_rect(self.par.vcm.get_frame_index(), x, y)
                self.im.add(ir)

                self.log("Manually Selected bounding box {0} on frame {1}".format(
                    ir.get_points(), ir.i))

                if self.im.has_n(2):
                    self.hint("Use keyboard controls to manipulate BBox {0} from frames {1} to {2}".format(
                        self.selected_id,
                        self.im[0].i,
                        self.im[1].i))

    def handle_keyboard(self, key_mapper: KeyMapper):
        par = self.par
        bbm = par.bbm
        if key_mapper.consume("i"):  # Select id
            id = PopUpWindow("Enter ID. If ID exists, will work on original").run()
            if id is None or id == "":
                self.cancel("Select ID", "Still on {0}".format(self.selected_id))
            else:
                try:
                    id = int(id)
                    self.log("Switched id from {0} to {1}".format(self.selected_id, id))
                    self.selected_id = id
                    self.reset_task()
                except:
                    self.error("Input ID not valid. Still on {0}".format(self.selected_id))
        elif key_mapper.consume("u"):  # Overwrite class
            if not bbm.has_id(self.selected_id):
                self.error("Could not update class. ID {0} does not exist".format(self.selected_id))
            else:
                cls = PopUpWindow("Enter new class for the selected object").run()
                prev = bbm.get_cls(self.selected_id)
                if cls == None:
                    self.cancel("Class change", "{0} still on class {1}".format(self.selected_id, prev))
                else:
                    bbm.add_or_update_id(self.selected_id, cls)
                    self.log("Class for ID {0} updated from {1} to {2}".format(
                        self.selected_id, prev, cls))
        elif key_mapper.consume("r"):
            self.reset_task()
            self.log("Selected bounding boxes reset".format(self.selected_id))
        elif key_mapper.consume("p"):
            deleted_ids = bbm.remove_unused_ids()
            self.log("Removed {0} ids without bounding boxes: {1}".format(len(deleted_ids), list(deleted_ids)))
        elif key_mapper.consume("z"):
            removed = self.im.remove_last()
            if removed is None:
                self.error("No input to remove")
            else:
                self.log("Removed last bounding box input on frame {0}".format(removed.i))
        elif key_mapper.consume("x"):
            removed = self.im.remove_last()
            if removed is None:
                self.error("No input to change")
            else:
                prev_i = removed.i
                removed.i = self.par.vcm.get_frame_index()
                self.im.add(removed)
                self.log("Moved last bounding box input from frame {0} to frame {1}".format(prev_i, removed.i))
        elif key_mapper.consume("q"):
            index = self.par.vcm.get_frame_index()
            retrived = bbm.get_last_bounding_box_i(self.selected_id, index)
            if retrived is None:
                self.error("Retrieving previous frame with bounding box failed")
            else:
                self.im.add(bbm.get_ir(self.selected_id, retrived))
        elif key_mapper.consume("e"):
            index = self.par.vcm.get_frame_index()
            retrived = bbm.get_next_bounding_box_i(self.selected_id, index)
            if retrived is None:
                self.error("Retrieving next frame with bounding box failed")
            else:
                self.im.add(bbm.get_ir(self.selected_id, retrived))
        elif key_mapper.consume("b"):
            if self.im.has_n(2):
                if not bbm.has_id(self.selected_id):
                    bbm.add_or_update_id(self.selected_id, self.DEFAULT_CLASS)
                    self.log("New id {0} for class {1} added".format(self.selected_id, self.DEFAULT_CLASS))
                bbm.replace_in_range(self.selected_id, *self.im.get_2_sorted())
                self.log("Bounding box for ID {0} set over index range [{1}, {2}]".format(
                    self.selected_id, self.im[0].i, self.im[1].i))
            elif self.im.has_n(1):
                if not bbm.has_id(self.selected_id):
                    bbm.add_or_update_id(self.selected_id, self.DEFAULT_CLASS)
                    self.log("New id {0} for class {1} added".format(self.selected_id, self.DEFAULT_CLASS))
                bbm.replace_in_range(self.selected_id, self.im.get_last(), self.im.get_last())
                self.log("Single bounding box for ID {0} set at {1}".format(
                    self.selected_id, self.im.get_last().i))
            else:
                self.error("Not enough inputs. Command ignored. Please draw at least 1 bounding box")
        elif key_mapper.consume("c"):
            if not self.im.has_n(2):
                self.error("Not enough inputs. Command ignored. Please click on 2 frames")
            elif not bbm.has_id(self.selected_id):
                self.error("Cannot clear bboxes - ID {0} does not exist".format(self.selected_id))
            else:
                i1 = self.im[0].i
                i2 = self.im[1].i
                bbm.clear_in_range(self.selected_id, i1, i2)
                self.log("Bbox for ID {0} cleared over index range [{1}, {2}]".format(self.selected_id, i1, i2))

                unused_ids = bbm.get_unused_ids()
                if len(unused_ids) > 0:
                    self.warn("Exists ids without bounding box: {0}".format(list(unused_ids)))
                    self.hint("Press p to remove")
        elif key_mapper.consume("v"):
            if not bbm.has_id(self.selected_id):
                self.error("Cannot clear bboxes - ID {0} does not exist".format(self.selected_id))
            else:
                i = self.par.vcm.get_frame_index()
                bbm.clear_in_range(self.selected_id, i, i)
                self.log("Bbox for ID {0} cleared for a single frame".format(self.selected_id, i))

                unused_ids = bbm.get_unused_ids()
                if len(unused_ids) > 0:
                    self.warn("Exists ids without bounding box: {0}".format(list(unused_ids)))
                    self.hint("Press p to remove")

    def reset_task(self):
        self.im.reset()
        self.irb.reset()

    def modify_frame(self, frame, i):
        if self.irb.has_initial_point():
            cv2.rectangle(frame, self.irb.get_initial_point(), self.mouse_position, **self.BOX_DRAWING_DISPLAY)
        return frame

    def get_state_message(self):
        bbm = self.par.bbm
        selected_msg = ""
        if self.im.has_n(2):
            selected_msg = "Input: {0} to {1}".format(self.im[0].i, self.im[1].i)
        elif self.im.has_n(1):
            selected_msg = "Input: {0}".format(self.im[0].i)
        elif self.im.has_n(0):
            selected_msg = "No Input"
        messages = [
            "BBox Mode:",
            "Target: {0} id {1} [{2}]".format(
                "existing" if bbm.has_id(self.selected_id) else "new",
                self.selected_id,
                bbm.get_cls(self.selected_id) if bbm.has_id(self.selected_id) else self.DEFAULT_CLASS
            ),
            selected_msg
        ]
        if self.irb.has_initial_point():
            messages.append("Drawing from {0}".format(self.irb.get_initial_point()))
            messages.append("Drawing to {0}".format(str(self.mouse_position)))

        return messages
