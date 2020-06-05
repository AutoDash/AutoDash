import cv2

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
    def __init__(self, bounding_boxes: list):
        self.bounding_boxes = [
            {
                1: [(50, 50), (100, 100)]
            }
        ]
        self.selected = set()

    def structure(self):
        pass

    def unstructure(self):
        pass

    def modify_frame(self, frame, i):
        i = 0
        for bi, (pt1, pt2) in self.bounding_boxes[i].items():
            if bi in self.selected:
                cv2.rectangle(frame, pt1, pt2, **self.BOX_DISPLAY)
            else:
                cv2.rectangle(frame, pt1, pt2, **self.SELECTED_BOX_DISPLAY)
            cv2.putText(frame, str(bi), (pt1[0] + 2, pt1[1] + 15), **self.BOX_I_DISPLAY)

        return frame

    def handleClickSelection(self, i, x, y):
        i = 0
        for bi, (pt1, pt2) in self.bounding_boxes[i].items():
            if pt1[0] < x < pt2[0] and pt1[1] < y < pt2[1]:
                if bi in self.selected:
                    self.selected.remove(bi)
                else:
                    self.selected.add(bi)