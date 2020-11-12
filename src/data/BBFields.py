from .Exceptions import InvalidData
import json

class BBFields:
    PARAMETERS = [
        "frames",
        "ids",
        "clss",
        "x1s",
        "y1s",
        "x2s",
        "y2s",
        "has_collision",
        "accident_locations"
    ]

    def __init__(self, **kwargs):
        self.set_fields_from_dict(kwargs)
    
    def __repr__(self) -> str:
        return json.dumps(self.to_json(), sort_keys=True, indent=2)

    def to_json(self):
        return dict(
            [(param, getattr(self, param)) for param in BBFields.PARAMETERS]
        )
    
    def get_row(self, idx):
        return [getattr(self,param)[idx] for param in BBFields.PARAMETERS]
    
    def __len__(self):
        return len(self.frames)
    
    def get_fields_as_list(self):
        return [getattr(self, param) for param in BBFields.PARAMETERS]

    def set_fields_from_list(self, lst):
        if len(lst) != len(self.PARAMETERS):
            raise InvalidData()
        self.set_fields_from_dict(dict(zip(self.PARAMETERS, lst)))
    
    def set_fields_from_dict(self, d):
        if d is None or len(d) == 0:
            for param in BBFields.PARAMETERS:
                setattr(self, param, [])
            return

        if "accident_locations" not in d:
            d["accident_locations"] = []

        for param in BBFields.PARAMETERS:
            if param in d and type(d[param]) == list:
                setattr(self, param, d[param])
                if len(getattr(self, BBFields.PARAMETERS[0])) \
                    != len(getattr(self, param)) and param != "accident_locations":
                    raise InvalidData(f"Length of all arrays must be equal")
            else:
                raise InvalidData("Invalid Bounding-Box, param: {0} missing".format(param))