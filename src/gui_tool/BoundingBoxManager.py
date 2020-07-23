import cv2
from collections import OrderedDict

class BoundingBoxManager(object):
    BOX_DISPLAY = {
        "color": (255, 255, 255),
        "lineType": 1,
        "thickness": 1
    }
    SELECTED_BOX_DISPLAY = {
        "color": (255, 255, 0),
        "lineType": 1,
        "thickness": 1
    }
    BOX_I_DISPLAY = {
        "fontFace": cv2.FONT_HERSHEY_SIMPLEX,
        "fontScale": 0.5,
        "color": (255, 255, 255)
    }
    def __init__(self, frames, ids, clss, x1s, y1s, x2s, y2s):
        self.bboxes = None
        self.id_to_cls = None
        self.selected = set()
        self.structure(frames, ids, clss, x1s, y1s, x2s, y2s)

    def structure(self, frames, ids, clss, x1s, y1s, x2s, y2s):
        self.bboxes = {}
        self.id_to_cls = {}
        for frame, id, cls, x1, y1, x2, y2 in zip(frames, ids, clss, x1s, y1s, x2s, y2s):
            self.id_to_cls[id] = cls
            frame = int(frame) - 1

            if id not in self.bboxes:
                self.bboxes[id] = {}
            self.bboxes[id][frame] = [(x1, y1), (x2, y2)]


    def unstructure(self):
        pass

    def modify_frame(self, frame, i):
        i = 0
        for id, frame_data in self.bboxes.items():
            p1, p2 = frame_data[i]
            if id in self.selected:
                cv2.rectangle(frame, p1, p2, **self.BOX_DISPLAY)
            else:
                cv2.rectangle(frame, p1, p2, **self.SELECTED_BOX_DISPLAY)
            cv2.putText(frame, str(id), (p1[0] + 2, p1[1] + 15), **self.BOX_I_DISPLAY)
        return frame

    def handleClickSelection(self, i, x, y):
        i = 0
        for id, frame_data in self.bboxes.items():
            p1, p2 = frame_data[i]
            if p1[0] < x < p2[0] and p1[1] < y < p2[1]:
                if id in self.selected:
                    self.selected.remove(id)
                else:
                    self.selected.add(id)

    def get_n_selected(self):
        return len(self.selected)
    def get_n_ids(self):
        return len(self.id_to_cls)
    def has_id(self, id):
        return id in self.id_to_cls