from executor.iExecutor import iExecutor
from service import ModelManager

class ObjectDetector(iExecutor):

    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)

    @classmethod
    def run(self, item):
        network = ModelManager.get_model("faster_rcnn_resnet101_kitti_2018_01_28")
        ids, scores, bboxes, masks = [X[0].asnumpy() for X in network(item.npy)]
        breakpoint()
