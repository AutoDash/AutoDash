from .Exceptions import InvalidData
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable


@dataclass
class BBox:
    frame: int
    x1: int
    y1: int
    x2: int
    y2: int

    def __init__(self, frame, x1, y1, x2, y2):
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        self.frame = frame
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def get_points(self):
        return (self.x1, self.y1), (self.x2, self.y2)

    def get_flat_points(self):
        return [self.x1, self.y1, self.x2, self.y2]

    def to_json(self):
        return (self.frame, self.x1, self.y1, self.x2, self.y2)

    def shift(self, amount):
        new_frame = self.frame + amount
        if new_frame < 0:
            raise RuntimeError("Trying to Shift frame to < 0")
        return BBox(self.frame + amount, *self.get_flat_points())

    def scale(self, ratio_x: float, ratio_y: float):
        return BBox(
            self.frame,
            int(self.x1 * ratio_x),
            int(self.y1 * ratio_y),
            int(self.x2 * ratio_x),
            int(self.y2 * ratio_y),
        )

    @staticmethod
    def from_json(arr):
        return BBox(*arr)


@dataclass
class BBObject:
    id: int
    has_collision: bool = False
    obj_class: str = ''
    bboxes: Dict[int, BBox] = field(default_factory=lambda: {})

    def set_bbox(self, frame_num: int, x1: int, y1: int, x2: int, y2: int):
        self.bboxes[frame_num] = BBox(frame_num, x1, y1, x2, y2)

    def __repr__(self):
        return f"""{{"class": {self.obj_class}, "bboxes": <bbox array of length {len(self.bboxes)}> }}"""

    def map_boxes(self, mapping_func: Callable[[BBox], Optional[BBox]]):
        new_bboxes = {}
        for i, box in self.bboxes.items():
            ret = mapping_func(box)
            if ret:
                new_bboxes[i] = ret
        self.bboxes = new_bboxes

    def clone(self):
        return BBObject.from_json(self.to_json())

    def to_json(self):
        return {
            'id': self.id,
            'has_collision': self.has_collision,
            'class': self.obj_class,
            'bboxes': [b.to_json() for b in self.bboxes.values()],
        }

    @staticmethod
    def from_json(obj):
        def __bbox_kvp_from_json(json):
            bbox = BBox.from_json(json)
            return (bbox.frame, bbox)

        bboxes = dict(map(__bbox_kvp_from_json, obj.get('bboxes', [])))
        return BBObject(obj['id'], obj['has_collision'], obj['class'], bboxes)


class BBFields:
    objects: Dict[int, BBObject]
    accident_locations: List[int]
    resolution: Tuple[int, int]
    _scale: Tuple[float, float]

    def __init__(self, objects={}, accident_locations=[], resolution=None):
        self.objects = objects
        self.accident_locations = accident_locations
        self.resolution = resolution
        self._scale = (1, 1)

    def __repr__(self):
        return f"""{{
        "objects":"{self.objects}",
        "accident_locations: {self.accident_locations},
        "resolution: {self.resolution},
        }}"""

    def items(self):
        return self.objects.items()

    def set_resolution(self, new_resolution: Tuple[int, int]):
        if not self.resolution or new_resolution == self.resolution:
            self.resolution = new_resolution
            self._scale = (1, 1)
            return

        ratio_x = new_resolution[0] / self.resolution[0]
        ratio_y = new_resolution[1] / self.resolution[1]

        def _scale_bbox(box):
            return box.scale(ratio_x, ratio_y)

        if ratio_x > 1 and ratio_y > 1:
            # new resolution is higher, scale existing boxes
            self.map_boxes(_scale_bbox)
            self.resolution = new_resolution
            self._scale = (1, 1)
        else:
            # new resolution is lower, scale any new bboxes
            self._scale = (ratio_x, ratio_y)

    def set_bbox(self, object_id: int, frame_num: int, x1: int, y1: int,
                 x2: int, y2: int):
        self.objects[object_id].set_bbox(
            frame_num,
            int(x1 / self._scale[0]),
            int(y1 / self._scale[1]),
            int(x2 / self._scale[0]),
            int(y2 / self._scale[1]),
        )

    def get_bbox(self, object_id: int, frame_num: int) -> Optional[BBox]:
        if (not object_id in self.objects
                or not frame_num in self.objects[object_id].bboxes):
            return None

        bbox = self.objects[object_id].bboxes[frame_num]

        return bbox.scale(*self._scale)

    def map_boxes(self, mapping_func: Callable[[BBox], Optional[BBox]]):
        for obj in self.objects.values():
            obj.map_boxes(mapping_func)

    def crop_range(self, start_i: int, end_i: int):
        def _crop(box: BBox) -> Optional[BBox]:
            if box.frame >= start_i and box.frame < end_i:
                return box.shift(-start_i)
            else:
                return None

        self.map_boxes(_crop)

        self.accident_locations = [
            x - start_i for x in self.accident_locations
            if x >= start_i and x < end_i
        ]
        return self

    def clear(self):
        self.objects.clear()
        self.accident_locations.clear()

    def has_collision(self):
        for obj in self.objects.values():
            if obj.has_collision:
                return True
        return False

    def get_bbs_for_frame(self, frame):
        ret = []
        for obj in self.objects.values():
            if frame in obj.bboxes:
                ret.append(obj.bboxes[frame])
        return ret

    def clone(self):
        return BBFields.from_json(self.to_json())

    def to_json(self):
        if not self.objects and not self.accident_locations:
            return None

        return {
            "objects": [v.to_json() for v in self.objects.values()],
            "accident_locations": self.accident_locations.copy(),
            "resolution": self.resolution,
        }

    def get_bbs_as_arrs(self):
        data = []
        for obj in self.objects.values():
            for box in obj.bboxes.values():
                data.append((
                    box.frame,
                    obj.id,
                    obj.obj_class,
                    box.x1,
                    box.y1,
                    box.x2,
                    box.y2,
                ))
        return data

    @staticmethod
    def from_json(json):
        def __BBObj_kvp_from_json(obj):
            ret = BBObject.from_json(obj)
            return (ret.id, ret)

        if not json:
            return BBFields()

        if "objects" in json:
            objects = dict(map(
                __BBObj_kvp_from_json,
                json['objects'],
            ))
            al = json.get('accident_locations', [])
            res = json.get('resolution', None)
            return BBFields(objects, al, res)
        else:  # for backwards compatability with old objects
            fields = BBFields({}, json.get('accident_locations', []))
            items = OldBBFields(**json)
            for i in range(len(items)):
                frame, id, clss, x1, y1, x2, y2, has_collision = items.get_row(
                    i)
                frame, x1, y1, x2, y2 = int(frame), int(x1), int(y1), int(
                    x2), int(y2)
                id = int(id)
                if id not in fields.objects:
                    fields.objects[id] = BBObject(id, bool(has_collision),
                                                  clss)
                fields.objects[id].bboxes[frame - 1] = BBox(
                    frame - 1,
                    x1,
                    y1,
                    x2,
                    y2,
                )
            return fields


class OldBBFields:
    PARAMETERS = [
        "frames",
        "ids",
        "clss",
        "x1s",
        "y1s",
        "x2s",
        "y2s",
        "has_collision",
    ]

    def __init__(self, **kwargs):
        self.set_fields_from_dict(kwargs)

    def __repr__(self) -> str:
        return json.dumps(self.to_json(), sort_keys=True, indent=2)

    def to_json(self):
        return dict([(param, getattr(self, param))
                     for param in self.PARAMETERS])

    def get_row(self, idx):
        return [getattr(self, param)[idx] for param in self.PARAMETERS]

    def __len__(self):
        return len(self.frames)

    def get_fields_as_list(self):
        return [getattr(self, param) for param in self.PARAMETERS]

    def set_fields_from_list(self, lst):
        if len(lst) != len(self.PARAMETERS):
            raise InvalidData()
        self.set_fields_from_dict(dict(zip(self.PARAMETERS, lst)))

    def set_fields_from_dict(self, d):
        if d is None or len(d) == 0:
            for param in self.PARAMETERS:
                setattr(self, param, [])
            return

        for param in self.PARAMETERS:
            if param in d and type(d[param]) == list:
                setattr(self, param, d[param])
                if len(getattr(self, self.PARAMETERS[0])) \
                        != len(getattr(self, param)):
                    raise InvalidData(f"Length of all arrays must be equal")
            else:
                raise InvalidData(
                    f"Invalid Bounding-Box, param: {param} missing")
