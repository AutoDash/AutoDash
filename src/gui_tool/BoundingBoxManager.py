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
    def __init__(self):
        self.bboxes = {}
        self.id_to_cls = {}
        self.selected = set()

    def set_to(self, frames, ids, clss, x1s, y1s, x2s, y2s, selected):
        self.bboxes = {}
        self.id_to_cls = {}
        for frame, id, cls, x1, y1, x2, y2, selected in zip(frames, ids, clss, x1s, y1s, x2s, y2s, selected):
            self.add_or_update_id(id, cls)

            frame = int(frame) - 1
            self.bboxes[id][frame] = [(x1, y1), (x2, y2)]

            if selected:
                self.selected.add(id)


    def extract(self):
        def format_frame(i):
            return "{0:0>5}".format(i+1)

        frames = []
        ids = []
        clss = []
        x1s = []
        y1s = []
        x2s = []
        y2s = []
        selected = []

        for id in self.bboxes.keys():
            for frame in self.bboxes[id]:
                frames.append(format_frame(frame))
                ids.append(id)
                clss.append(self.get_cls(id))
                x1s.append(self.bboxes[id][frame][0][0])
                y1s.append(self.bboxes[id][frame][0][1])
                x2s.append(self.bboxes[id][frame][1][0])
                y2s.append(self.bboxes[id][frame][1][1])
                selected.append(1 if id in self.selected else 0)

        return frames, ids, clss, x1s, y1s, x2s, y2s, selected



    def modify_frame(self, frame, i):
        for id, frame_data in self.bboxes.items():
            if i in frame_data:
                p1, p2 = frame_data[i]
                if id in self.selected:
                    cv2.rectangle(frame, p1, p2, **self.SELECTED_BOX_DISPLAY)
                else:
                    cv2.rectangle(frame, p1, p2, **self.BOX_DISPLAY)
                cv2.putText(frame, str(id), (p1[0] + 2, p1[1] + 15), **self.BOX_I_DISPLAY)
        return frame

    def handleClickSelection(self, i, x, y):
        for id, frame_data in self.bboxes.items():
            if i in frame_data:
                p1, p2 = frame_data[i]
                if p1[0] < x < p2[0] and p1[1] < y < p2[1]:
                    if id in self.selected:
                        self.selected.remove(id)
                    else:
                        self.selected.add(id)
                    return id
        return None

    def replace_in_range(self, id, i1, pts1, i2, pts2):
        if i2 < i1:
            i1, pts1, i2, pts2 = i2, pts2, i1, pts1

        r = i2-i1
        if r == 0:
            r = 1

        # Unravel
        pts1 = [pts1[0][0], pts1[0][1], pts1[1][0], pts1[1][1]]
        pts2 = [pts2[0][0], pts2[0][1], pts2[1][0], pts2[1][1]]

        if pts1[0] > pts1[2]: pts1[0], pts1[2] = pts1[2], pts1[0]
        if pts2[0] > pts2[2]: pts2[0], pts2[2] = pts2[2], pts2[0]
        if pts1[1] > pts1[3]: pts1[1], pts1[3] = pts1[3], pts1[1]
        if pts2[1] > pts2[3]: pts2[1], pts2[3] = pts2[3], pts2[1]

        slopes = [(pts2[i] - pts1[i]) / r for i in range(4)]

        for o in range(i2-i1+1):
            frame = i1+o
            new_pt = [pts1[i] + int(slopes[i]*o) for i in range(4)]
            self.bboxes[id][frame] = (new_pt[0], new_pt[1]), (new_pt[2], new_pt[3])

    def clear_in_range(self, id, i1, i2):
        if i2 < i1:
            i1, i2 = i2, i1
        for i in range(i1, i2+1):
            if i in self.bboxes[id]:
                del self.bboxes[id][i]

    def add_or_update_id(self, id, cls):
        self.id_to_cls[id] = cls
        if id not in self.bboxes:
            self.bboxes[id] = {}
    def get_is_selected(self, id):
        return id in self.selected
    def get_n_selected(self):
        return len(self.selected)
    def get_n_ids(self):
        return len(self.id_to_cls)
    def has_id(self, id):
        return id in self.bboxes
    def get_cls(self, id):
        if id in self.id_to_cls:
            return self.id_to_cls[id]
        return None
    def get_unused_ids(self):
        unused_ids = set()
        for id, d in self.bboxes.items():
            if len(d) == 0:
                unused_ids.add(id)
        for id in self.id_to_cls.keys():
            if id not in self.bboxes:
                unused_ids.add(id)
        return unused_ids

    def remove_unused_ids(self):
        unused_ids = self.get_unused_ids()
        for i in unused_ids:
            if i in self.bboxes:
                del self.bboxes[i]
            if i in self.id_to_cls:
                del self.id_to_cls[i]
        return unused_ids



