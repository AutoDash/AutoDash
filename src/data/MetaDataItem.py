import json, hashlib

import os


class MetaDataItem:
    def __init__(self, id, title, url, collision_type, description, location):
        self.id = id
        self.title = title
        self.url = url
        self.collision_type = collision_type
        self.description = description
        self.location = location

    def __repr__(self) -> str:
        return self.to_json_str()

    def encode(self) -> str:
        return hashlib.sha224(self.url.encode()).hexdigest()

    def to_json(self) -> dict:
        return {
            'title': self.title,
            'url': self.url,
            'collision_type': self.collision_type,
            'description': self.description,
            'location': self.location
        }

    def to_json_str(self) -> str:
        return json.dumps(self.to_json(), sort_keys=True, indent=2)

    # For storing local storage in file system
    def to_file(self, directory: str):
        store_loc = os.path.join(directory, gen_filename(self.id))
        # Write the output to disk
        with open(store_loc, 'w') as outfile:
            json.dump(self.to_json(), outfile, sort_keys=True, indent=2)

# For accessing metadata items stored in local storage
def metadata_from_file(filename: str, directory: str) -> MetaDataItem:
    loc = os.path.join(directory, filename)
    with open(loc) as file:
        data = json.load(file)
        data['id'] = get_id_from_filename(filename)
        return MetaDataItem(**data)


def gen_filename(id: str):
    return id + '_metadata.json'

def get_id_from_filename(filename: str):
    return filename.split('_')[0]