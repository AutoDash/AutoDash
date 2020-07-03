from src.executor.iExecutor import iExecutor
from gluoncv import model_zoo

class ObjectDetector(iExecutor):

    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)
        self._network = model_zoo.get_model('mask_rcnn_resnet50_v1b_coco', pretrained=True)

    @classmethod
    def run(self, item : VideoItem):
        ids, scores, bboxes, masks = [X[0].asnumpy() for X in net(item.npy)]
        breakpoint()
