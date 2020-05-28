from typing import Union
import json, hashlib

import os

class MetaDataItem:
    def __init__(self, title, url, download_src, id=None, collision_type=None, description=None, location=None, accident_index=None, is_dashcam=None, tags={}):
        self.id = id
        self.title = title
        self.url = url
        self.collision_type = collision_type
        self.description = description
        self.location = location
        self.download_src = download_src
        self.accident_index = accident_index
        self.is_dashcam = is_dashcam

        if tags is None:
            self.tags = {}
        else:
            self.tags = tags


    def __repr__(self) -> str:
        return self.to_json_str()

    # Returns lists of attributes and their types. Types should ideally be default constructable.
    @staticmethod
    def attributes() -> dict:
        return {
            'title': str,
            'url' : str,
            'download_src': str,
            'collision_type' : str,
            'description' : str,
            'location' : str,
            'accident_index': int,
            'is_dashcam': bool,
            'tags': dict
        }
      
    def encode(self) -> str:
        return hashlib.sha224(self.url.encode()).hexdigest()

    def to_json(self) -> dict:
        return {
            'title': self.title,
            'url': self.url,
            'download_src': self.download_src,
            'collision_type': self.collision_type,
            'description': self.description,
            'location': self.location,
            'accident_index': self.accident_index,
            'is_dashcam': self.is_dashcam,
            'tags': self.tags
        }

    def to_json_str(self) -> str:
        return json.dumps(self.to_json(), sort_keys=True, indent=2)

    # For storing local storage in file system
    def to_file(self, directory: str):
        store_loc = os.path.join(directory, gen_filename(self.id))
        # Write the output to disk
        with open(store_loc, 'w') as outfile:
            json.dump(self.to_json(), outfile, sort_keys=True, indent=2)

    def add_tag(self, name: str, val: Union[dict, str]):
        if name in self.tags.keys() and isinstance(self.tags[name], dict) and isinstance(val, dict):
            self.tags[name].update(val)
        else:
            self.tags[name] = val


# For accessing metadata items stored in local storage
def metadata_from_file(filename: str, directory: str) -> MetaDataItem:
    loc = os.path.join(directory, filename)
    with open(loc) as file:
        data = json.load(file)
        data['id'] = get_id_from_filename(filename)
        return MetaDataItem(**data)

def delete_metadata_file(id: str, directory: str):
    loc = os.path.join(directory, gen_filename(id))
    if os.path.exists(loc):
        os.remove(loc)

def gen_filename(id: str):
    return id + '_metadata.json'

def get_id_from_filename(filename: str):
    return filename.split('_')[0]

