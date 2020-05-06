import json
from typing import Union


class MetaDataItem:
    def __init__(self, id, title, url, collision_type, description, location):
        self.id = id
        self.title = title
        self.url = url
        self.collision_type = collision_type
        self.description = description
        self.location = location
        self.tags = {}

    def __repr__(self) -> str:
        return self.to_json_str()

    def to_json(self) -> dict:
        return {
            'title': self.title,
            'url': self.url,
            'collision_type': self.collision_type,
            'description': self.description,
            'location': self.location,
            'tags': self.tags
        }

    def to_json_str(self) -> str:
        return json.dumps(self.to_json(), sort_keys=True, indent=2)
    
    def to_file(self):
        # Write the output to disk
        with open(self.id + '_metadata.json', 'w') as outfile:
            json.dump(self.to_json, outfile, sort_keys=True, indent=2)

    def add_tag(self, name: str, val: Union[dict, str]):
        if name in self.tags.keys() and isinstance(self.tags[name], dict) and isinstance(val, dict):
            self.tags[name].update(val)
        else:
            self.tags[name] = val
