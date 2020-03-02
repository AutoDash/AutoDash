import json

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


def create_metadata(id: str, variables: dict) -> MetaDataItem:
    metadata = MetaDataItem(id,
                            variables['title'],
                            variables['url'],
                            variables['collision_type'],
                            variables['description'],
                            variables['location'])
    return metadata

