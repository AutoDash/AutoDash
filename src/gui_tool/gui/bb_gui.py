from src.gui_tool.utils.key_mapper import KeyMapper
from .context import GUIContext
from .bb.BoundingBoxManager import BoundingBoxManager
from .tinker_subuis.additional_tags import AdditionalTagWindow
from .tinker_subuis.text_popup import TextPopup
import cv2
from gui_tool.gui.bb.BoundingBoxInputManager import IndexedRectBuilder, BoundingBoxInputManager

from .general_gui import VideoPlayerGUIManager
from .gui_mode import InternalMode

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

class BBGUIManager(VideoPlayerGUIManager):
    WINDOW_NAME = 'tagger'

    LOG_LINES = 6
    LOG_LINE_HEIGHT = 17
    LOG_LINE_MARGIN = 2
    LOG_START_X = 250
    IMG_STARTING_Y = LOG_LINE_HEIGHT * LOG_LINES + LOG_LINE_MARGIN * (LOG_LINES + 1) + 3

    def __init__(self, context: GUIContext):
        super(BBGUIManager, self).__init__(context,
           [
               InternaSelectionMode(self),
               InternalBBoxMode(self)
           ]
        )
        self.bbm = BoundingBoxManager(self.vcm.get_frames_count())
        self.bbm.set_to(*context.get_bbox_fields_as_list())

    def start(self):
        super(BBGUIManager, self).start()
        self.context.set_bbox_fields_from_list(self.bbm.extract())

    def modify_frame(self, frame, frame_index):
        frame = self.bbm.modify_frame(frame, frame_index)
        return frame

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
            id = TextPopup("Enter ID. If ID exists, will work on original").run()
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
                cls = TextPopup("Enter new class for the selected object").run()
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
