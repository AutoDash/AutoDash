from lib.anonymization.auto_face_blurring import AutoFaceBlurrer
from ..data.VideoItem import VideoItem
from .iExecutor import iExecutor


class FaceBlurrer(iExecutor):
    def run(self, item: VideoItem):
        # Run the automatic face blurring tool on the input video with a confidence threshold
        # of 0.10, enlarge factor of 0.2, skip frames = 1, frame buffer size of 1024, and overwrite = True.
        # The output video will overwrite the input filepath.
        blurrer = AutoFaceBlurrer(item.filepath, item.filepath, "0.10", "0.2", "1", "1024", "True")
        blurrer.run()
        return item
