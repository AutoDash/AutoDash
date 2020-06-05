import numpy as np
import cv2

class VideoTaggingResults(object):
    def __init__(self):
        self.is_dashcam = None
        self.accident_frame_number = None
        self.marked = None
        self.unmark()

    def __str__(self):
        if not self.marked:
            return "Unset"
        if not self.is_dashcam:
            return "Is not dashcam"
        if self.accident_frame_number is None:
            return "No accident exists"
        if self.accident_frame_number is not None:
            return "Accident on frame {0}".format(self.accident_frame_number)
        return "Impossible state"

    def mark_accident(self, frame_number: int):
        self.marked = True
        self.accident_frame_number = frame_number


    def mark_not_dashcam(self):
        self.marked = True
        self.is_dashcam = False

    def unmark(self):
        self.is_dashcam = True
        self.accident_frame_number = None
        self.marked = False

class VideoCaptureManager(object):
    def __init__(self, file_loc: str):
        self.file_loc = file_loc
        self.capture = None
        self.n_frames_total = None
        self.n_frames_played = None
        self.current_frame = None
        self.paused = False

    def _set_capture(self, skip_n: int = 0):
        if self.capture is not None:
            self.capture.release()
        skip_n = int(skip_n)
        self.capture = cv2.VideoCapture(self.file_loc)

        self.n_frames_total = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.n_frames_played = skip_n

        if skip_n > 0:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, skip_n-1)
            ret, self.current_frame = self.capture.read()

    def start_from(self, location: int = 0):
        self._set_capture(location)

    def shift_frame_index(self, shift: int):
        self._set_capture(
            max(
                min(
                    self.get_current_frame_index() + shift,
                    self.get_total_frames()
                ),
                0
            )
        )

    def release(self):
        self.capture.release()

    def next(self) -> np.ndarray:
        if not self.paused and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                self.current_frame = frame
                self.n_frames_played += 1
        return self.current_frame

    def get_total_frames(self) -> int:
        return self.n_frames_total
    def get_current_frame_index(self) -> int:
        return self.n_frames_played
    def get_paused(self) -> bool:
        return self.paused
    def set_paused(self, paused: bool) -> bool:
        self.paused = paused
    def is_open(self) -> bool:
        return self.capture.isOpened() and \
               (self.get_current_frame_index() != self.get_total_frames() or self.get_paused())

class VideoPlayerGUIManager(object):
    PROGRESS_BAR_NAME = "progress"
    FRAME_RATE_BAR_NAME = "frame_delay"
    PAUSE_BUTTON_NAME = "pause"
    WINDOW_NAME = 'tagger'

    def __init__(self, file_loc: str):
        self.vcm = VideoCaptureManager(file_loc)
        self.vcm.start_from(0)
        self.frame_rate = 25
        self.result = VideoTaggingResults()


    def start(self) -> VideoTaggingResults:
        self.set_GUI()
        self.play_video()
        self.cleanup()
        return self.result

    def set_GUI(self):
        cv2.namedWindow(self.WINDOW_NAME)

        def set_frame_rate_callback(value):
            self.frame_rate = max(1, value)
        def set_progress_rate_callback(value):
            if abs(value - self.vcm.get_current_frame_index()) < 5:
                return
            self.vcm.start_from(value)
        def set_paused_callback(value):
            if self.vcm is not None:
                self.vcm.set_paused(value)

        cv2.createTrackbar(self.PROGRESS_BAR_NAME, self.WINDOW_NAME, 1, self.vcm.get_total_frames(),
                           set_progress_rate_callback)
        cv2.createTrackbar(self.FRAME_RATE_BAR_NAME, self.WINDOW_NAME,
                           self.frame_rate, 60, set_frame_rate_callback)
        cv2.createTrackbar(self.PAUSE_BUTTON_NAME,  self.WINDOW_NAME,
                           False, 1, set_paused_callback)

    def play_video(self):
        while self.vcm.is_open():
            frame = self.vcm.next()
            displayed = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
            cv2.imshow(self.WINDOW_NAME, displayed)

            cv2.setTrackbarPos(self.PROGRESS_BAR_NAME, self.WINDOW_NAME, self.vcm.get_current_frame_index())

            mark_changed = False
            received_key = cv2.waitKey(self.frame_rate) & 0xFF
            if received_key == 27:  # Escape key
                break
            elif received_key == ord("a"):
                self.vcm.shift_frame_index(-1)
            elif received_key == ord("s"):
                self.vcm.shift_frame_index(-10)
            elif received_key == ord("d"):
                self.vcm.shift_frame_index(1)
            elif received_key == ord("w"):
                self.vcm.shift_frame_index(10)
            elif received_key == ord(" "):
                cv2.setTrackbarPos(self.PAUSE_BUTTON_NAME, self.WINDOW_NAME, not self.vcm.get_paused())
            elif received_key == ord("u"):
                self.result.unmark()
                mark_changed = True
            elif received_key == ord("n"):
                self.result.mark_not_dashcam()
                mark_changed = True
            elif received_key == ord("m"):
                self.result.mark_accident(self.vcm.get_current_frame_index())
                mark_changed = True
            if mark_changed:
                print("Marked {0} with {1}".format(self.vcm.file_loc, self.result))


    def cleanup(self):
        self.vcm.release()
        cv2.destroyAllWindows()


