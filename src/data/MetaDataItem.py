from typing import Union
from .BBFields import BBFields
import json
import hashlib
import copy
from datetime import datetime

import os


class MetaDataItem:
    def __init__(self, **kwargs):
        self.title = kwargs["title"]
        self.url = kwargs["url"]
        self.download_src = kwargs["download_src"]
        self.date_created = kwargs.get("date_created", get_current_time_epoch_millis())
        self.id = kwargs.get("id")
        print(f'Parsing item {self.id}')
        self.collision_type = kwargs.get("collision_type")
        self.description = kwargs.get("description")
        self.location = kwargs.get("location")
        self.tags = kwargs.get("tags", {})
        self.enum_tags = kwargs.get("enum_tags", [])
        self.is_cancelled = kwargs.get("is_cancelled", False)
        self.is_split_url = kwargs.get("is_split_url", False)
        self.reckless_intervals = kwargs.get("reckless_intervals", [])
        self.to_be_deleted = kwargs.get("to_be_deleted", False)

        accident_locations = kwargs.get("accident_locations", [])

        bb_fields_json = kwargs.get("bb_fields", {})

        # prioritize existing collision_locations in data
        if accident_locations:
            if "collision_locations" not in bb_fields_json:
                bb_fields_json["collision_locations"] = accident_locations
        self.bb_fields = BBFields.from_json(bb_fields_json)

        self.start_i = kwargs.get("start_i")
        self.end_i = kwargs.get("end_i")

    def __repr__(self) -> str:
        return f"Metadata {self.id}:\n\n" + f"""
{{
    'title': {self.title},
    'url': {self.url},
    'download_src': {self.download_src},
    'date_created': {self.date_created},
    'collision_type': {self.collision_type},
    'description': {self.description},
    'location': {self.location},
    'id': {self.id},
    'is_cancelled': {self.is_cancelled},
    'is_split_url': {self.is_split_url},
    'tags': {self.tags},
    'enum_tags': {self.enum_tags},
    'bb_fields': {self.bb_fields},
    'start_i': {self.start_i},
    'end_i': {self.end_i},
    'reckless_intervals': {self.reckless_intervals},
    'to_be_deleted': {self.to_be_deleted},
}}
"""

    # Returns lists of attributes and their types. Types should ideally be default constructable.
    @staticmethod
    def attributes() -> dict:
        return {
            'title': str,
            'url': str,
            'download_src': str,
            'date_created': int,
            'collision_type': str,
            'description': str,
            'location': str,
            'tags': dict,
            'id': str,
            'enum_tags': list,
            'is_cancelled': bool,
            'is_split_url': bool,
            'bb_fields': dict,
            'start_i': int,
            'end_i': int,
            'reckless_intervals': list,
            'to_be_deleted': bool,
        }

    def encode(self) -> str:
        return hashlib.sha224(self.url.encode()).hexdigest()

    def to_json(self) -> dict:
        return {
            'title': self.title,
            'url': self.url,
            'download_src': self.download_src,
            'date_created': self.date_created,
            'collision_type': self.collision_type,
            'description': self.description,
            'location': self.location,
            'id': self.id,
            'is_cancelled': self.is_cancelled,
            'is_split_url': self.is_split_url,
            'tags': copy.deepcopy(self.tags),
            'enum_tags': self.enum_tags,
            'bb_fields': self.bb_fields.to_json(),
            'start_i': self.start_i,
            'end_i': self.end_i,
            'reckless_intervals': self.reckless_intervals,
            'to_be_deleted': self.to_be_deleted,
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
        if name in self.tags.keys() and isinstance(
                self.tags[name], dict) and isinstance(val, dict):
            self.tags[name].update(val)
        else:
            self.tags[name] = val

    def get_tag(self, name: str):
        if name in self.tags.keys():
            return self.tags[name]
        else:
            return None

    def clone(self):
        m = MetaDataItem(**self.to_json())
        m.id = None
        return m


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


# Get current time in UTC since Unix epoch
def get_current_time_epoch_millis():
    epoch = datetime.utcfromtimestamp(0)
    return int((datetime.utcnow() - epoch).total_seconds() * 1000)
