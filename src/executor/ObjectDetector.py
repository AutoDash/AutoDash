from .iExecutor import iExecutor
from ..service import ModelManager
import numpy as np
import tensorflow as tf
from pprint import pprint
from ..signals import CancelSignal

class ObjectDetector(iExecutor):

    def __init__(self, 
            *parents,
            skip_n = 0,
            batch_size = 1, 
            confidence_threshold = 0.5):
        super().__init__(*parents)
        self.skip_n = skip_n
        self.batch_size = batch_size
        self.confidence_threshold = confidence_threshold

    def run(self, item):
        item.labels = {
            'frames': [],
            'boxes': [],
            'classes': []
        }
        imported = ModelManager.get_model("faster_rcnn_resnet101_kitti_2018_01_28")
        network = imported.signatures['serving_default']
        X = np.asarray(item.npy)
        n_batches = int(X.shape[0] / self.batch_size)
        print(f"[ObjectDetector] Number of batches: {n_batches}")
        for i in range(0, n_batches):
            X_b = X[i * self.batch_size : (i+1) * self.batch_size]
            if self.skip_n > 0:
                X_b = X_b[::self.skip_n]
            Y = network(tf.convert_to_tensor(X_b))
            if i % (n_batches // 20) == 0:
                print(f"[ObjectDetector] {int(100 * i / n_batches)}% completed")
            detections = Y['detection_scores'] > self.confidence_threshold
            if np.any(detections):
                classes = Y['detection_classes'][detections]
                boxes = Y['detection_boxes'][detections]
                frames = np.arange(i * self.batch_size, (i+1) * self.batch_size)
                if self.skip_n > 0:
                    frames = frames[::self.skip_n]
                frames = frames[np.any(Y['detection_scores'] > self.confidence_threshold, axis=1)]
                item.labels['frames'] += frames.tolist()
                item.labels['classes'].append(classes.numpy().tolist())
                item.labels['boxes'].append(boxes.numpy().tolist())
        print("[ObjectDetector] done")
        return item
