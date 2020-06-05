from ..executor.iExecutor import iExecutor
from ..service.ModelManager import ModelManager
from ..data.VideoItem import VideoItem
from ..service import model_manager as ModelManager

class BinaryFilter(iExecutor):
    def __init__(self, parents, model_id)
        super().__init__(*parents)
        self.model = ModelManager.get_model(model_id)
        

    def run(self, item : VideoItem):
        prediction = self.model.predict(item.video_data)
        if prediction < 0.5:
            # TODO: Filter out
            pass
