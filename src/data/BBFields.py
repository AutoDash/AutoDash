from .Exceptions import InvalidData
import json
from dataclasses import dataclass, field
from typing import List, Dict


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

    @staticmethod
    def from_json(arr):
        return BBox(*arr)


@dataclass
class BBObject:
    id: int
    has_collision: bool = False
    obj_class: str = ''
    bboxes: Dict[int, BBox] = field(default_factory=lambda: {})

    def __repr__(self):
        return f"""{{"class": {self.obj_class}, "bboxes": <bbox array of length {len(self.bboxes)}> }}"""

    def crop_range(self, start_i, end_i):
        new_bboxes = {}
        for i, box in self.bboxes.items():
            if box.frame >= start_i and box.frame < end_i:
                new_bboxes[i] = box.shift(-start_i)
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

        bboxes = dict(map(__bbox_kvp_from_json, obj['bboxes']))
        return BBObject(obj['id'], obj['has_collision'], obj['class'], bboxes)


class BBFields:
    objects: Dict[int, BBObject]
    accident_locations: List[int]

    def __init__(self, objects={}, accident_locations=[]):
        self.objects = objects
        self.accident_locations = accident_locations

    def __repr__(self):
        return f"""{{
        "objects":"{self.objects}",
        "accident_locations: {self.accident_locations}
        }}"""

    def items(self):
        return self.objects.items()

    def crop_range(self, start_i, end_i):
        for obj in self.objects.values():
            obj.crop_range(start_i, end_i)
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
        return {
            "objects": [v.to_json() for v in self.objects.values()],
            "accident_locations": self.accident_locations.copy(),
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
            return BBFields(objects, json.get('accident_locations', []))
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
