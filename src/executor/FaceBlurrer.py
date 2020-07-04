from lib.anonymization.auto_face_blurring import AutoFaceBlurrer
from data.VideoItem import VideoItem
from executor.iExecutor import iExecutor


class FaceBlurrer(iExecutor):
    def run(self, item: VideoItem):
        # TODO: verify output path
        blurrer = AutoFaceBlurrer(item.filepath, item.filepath, "0.05", "0.2", "2", "1024")
        blurrer.run()
        return item
