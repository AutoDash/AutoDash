import cv2
from ...utils.IndexedRect import IndexedRect
from ....data.BBFields import BBox, BBObject
from ..bb_context import BBContext


class BoundingBoxManager(object):
    BOX_DISPLAY = {"color": (255, 255, 255), "lineType": 1, "thickness": 1}
    SELECTED_BOX_DISPLAY = {
        "color": (255, 255, 0),
        "lineType": 1,
        "thickness": 1
    }
    COLLISION_LOCATION_BOX_DISPLAY = {
        "color": (0, 255, 255),
        "lineType": 1,
        "thickness": 2
    }
    BOX_I_DISPLAY = {
        "fontFace": cv2.FONT_HERSHEY_SIMPLEX,
        "fontScale": 0.5,
        "color": (255, 255, 255)
    }

    def __init__(self, total_frames):
        self.id_to_cls = {}
        self.selected = set()
        self.collision_locations = []
        self.total_frames = total_frames

    def set_to(self, context: BBContext, selected):
        self.selected.update(selected)
        self.bbox_fields = context.bbox_fields
        self.objects = context.bbox_fields.objects
        self.collision_locations = self.bbox_fields.collision_locations
        self.collision_locations.sort()

    def modify_frame(self, frame, i):
        for id, obj in self.objects.items():
            if i in obj.bboxes:
                p1, p2 = obj.bboxes[i].get_points()
                if id in self.selected:
                    if i in self.collision_locations:
                        cv2.rectangle(frame, p1, p2,
                                      **self.COLLISION_LOCATION_BOX_DISPLAY)
                    else:
                        cv2.rectangle(frame, p1, p2,
                                      **self.SELECTED_BOX_DISPLAY)
                else:
                    cv2.rectangle(frame, p1, p2, **self.BOX_DISPLAY)
                cv2.putText(frame, str(id), (p1[0] + 2, p1[1] + 15),
                            **self.BOX_I_DISPLAY)
        return frame

    def handleClickSelection(self, i, x, y):
        for id in self.objects:
            bbox = self.bbox_fields.get_bbox(id, i)
            if bbox:
                p1, p2 = bbox.get_points()
                if p1[0] < x < p2[0] and p1[1] < y < p2[1]:
                    if id in self.selected:
                        self.selected.remove(id)
                    else:
                        self.selected.add(id)
                    return id
        return None

    def replace_in_range(self, id, ir1: IndexedRect, ir2: IndexedRect):
        r = ir2.i - ir1.i
        if r == 0:
            r = 1

        # Unravel
        pts1 = ir1.get_flat_points()
        pts2 = ir2.get_flat_points()

        slopes = [(pts2[i] - pts1[i]) / r for i in range(4)]

        for o in range(ir2.i - ir1.i + 1):
            frame = ir1.i + o
            new_pt = [pts1[i] + int(slopes[i] * o) for i in range(4)]
            self.bbox_fields.set_bbox(
                id,
                frame,
                new_pt[0],
                new_pt[1],
                new_pt[2],
                new_pt[3],
            )

    def clear_in_range(self, id, i1, i2):
        if i2 < i1:
            i1, i2 = i2, i1
        for i in range(i1, i2 + 1):
            if i in self.objects[id].bboxes:
                del self.objects[id].bboxes[i]

    def add_or_update_id(self, id, cls):
        if id not in self.objects:
            self.objects[id] = BBObject(id)
        self.objects[id].obj_class = cls

    def get_is_selected(self, id):
        return id in self.selected

    def get_n_selected(self):
        return len(self.selected)

    def get_n_ids(self):
        return len(self.objects)

    def has_id(self, id):
        return id in self.objects

    def get_cls(self, id):
        if self.has_id(id):
            return self.objects[id].obj_class
        return None

    def get_unused_ids(self):
        unused_ids = set()
        for id, d in self.objects.items():
            if not d.bboxes or not d.obj_class:
                unused_ids.add(id)
        return unused_ids

    def remove_unused_ids(self):
        unused_ids = self.get_unused_ids()
        for i in unused_ids:
            if i in self.objects:
                del self.objects[i]
        return unused_ids

    def get_last_bounding_box_i(self, id, starting_i):
        if id not in self.objects:
            return None
        for i in range(starting_i, -1, -1):
            if i in self.objects[id].bboxes:
                return i
        return None

    def get_next_bounding_box_i(self, id, starting_i):
        if id not in self.objects:
            return None
        for i in range(starting_i, self.total_frames):
            if i in self.objects[id].bboxes:
                return i
        return None

    def get_ir(self, id, i):
        if id not in self.objects or i not in self.objects[id].bboxes:
            return None
        bbox = self.objects[id].bboxes[i]
        return IndexedRect(bbox.frame, *bbox.get_flat_points())

    def add_collision_location(self, loc):
        if loc not in self.collision_locations:
            self.collision_locations.append(loc)
            self.collision_locations.sort()

    def remove_collision_location(self, loc):
        for i, val in enumerate(self.collision_locations):
            if val == loc:
                del self.collision_locations[i]
                break

    def has_collision_location(self, loc):
        return loc in self.collision_locations

    def get_collision_locations(self):
        return self.collision_locations.copy()

    def clear_bounding_boxes(self):
        self.bbox_fields.clear()