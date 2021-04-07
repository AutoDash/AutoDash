from src.data.MetaDataItem import MetaDataItem

def sample_mdi_dict():
    return {
        "title": "title",
        "url": "www.website.ca",
        "download_src": "website",
        "date_created": 5,
        "reckless_intervals": [],
        "id": "5",
        'collision_type': None,
        'description': None,
        'start_i': 0,
        'end_i': 100,
        'enum_tags': ["enum_tag1", "enum_tag2"],
        'is_cancelled': False,
        'is_split_url': False,
        'to_be_deleted': False,
        'location': None,
        'tags': {
            "tag1": "val1"
        },
        "bb_fields": {
            "collision_locations": [1, 10, 100],
            "objects": [{
                "id": 1,
                "has_collision": True,
                "class": "car",
                "bboxes": [{"frame": 0, "x1": 1, "y1": 2, "x2": 3,"y2": 4}],
            }, {
                "id": 2,
                "has_collision": False,
                "class": "truck",
                "bboxes": [{"frame": 0, "x1": 5, "y1": 6, "x2": 7,"y2": 8}],
            }],
            "resolution":
            None
        }
    }


def sample_mdi():
    return MetaDataItem(**sample_mdi_dict())