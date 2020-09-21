from .general_gui import VideoPlayerGUIManager
from ..utils.key_mapper import KeyMapper

class InternalMode(object):
    def __init__(self, parent: VideoPlayerGUIManager, instructions: list):
        self.par = parent
        self.INSTRUCTIONS = instructions
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