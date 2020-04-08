import json, hashlib

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

    # Returns lists of attributes and their types. Types should ideally be default constructable.
    @staticmethod
    def attributes() -> dict:
        return {
            'title': str,
            'url' : str,
            'collision_type' : str,
            'description' : str,
            'location' : str
        }
      
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

    def to_file(self):
        # Write the output to disk
        with open(self.id + '_metadata.json', 'w') as outfile:
            json.dump(self.to_json, outfile, sort_keys=True, indent=2)
