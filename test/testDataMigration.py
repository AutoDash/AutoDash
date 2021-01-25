#!/usr/bin/env python3
import unittest
from src.data.MetaDataItem import MetaDataItem


class TestDataMigration(unittest.TestCase):
    def test_old_to_new_metadata(self):
        self.maxDiff = None
        old_mdi = {
            "accident_locations": [1, 10, 100],
            "title": "title",
            "url": "www.website.ca",
            "download_src": "website",
            "id": "5",
            'collision_type': None,
            'description': None,
            'start_i': 0,
            'end_i': 100,
            'enum_tags': ["enum_tag1", "enum_tag2"],
            'is_cancelled': False,
            'is_split_url': False,
            'location': None,
            'state': None,
            'tags': {
                "tag1": "val1"
            },
            "bb_fields": {
                "frames": ["0001", "0001"],
                "ids": ["1", "2"],
                "clss": ["car", "truck"],
                "x1s": [1, 5],
                "y1s": [2, 6],
                "x2s": [3, 7],
                "y2s": [4, 8],
                "has_collision": [1, 0],
            }
        }

        expected_new_mdi = {
            "title": "title",
            "url": "www.website.ca",
            "download_src": "website",
            "id": "5",
            'collision_type': None,
            'description': None,
            'start_i': 0,
            'end_i': 100,
            'enum_tags': ["enum_tag1", "enum_tag2"],
            'is_cancelled': False,
            'is_split_url': False,
            'location': None,
            'state': None,
            'tags': {
                "tag1": "val1"
            },
            "bb_fields": {
                "collision_locations": [1, 10, 100],
                "objects": [{
                    "id": 1,
                    "has_collision": True,
                    "class": "car",
                    "bboxes": [(0, 1, 2, 3, 4)],
                }, {
                    "id": 2,
                    "has_collision": False,
                    "class": "truck",
                    "bboxes": [(0, 5, 6, 7, 8)],
                }],
                "resolution":
                None
            }
        }

        mdi = MetaDataItem(**old_mdi)
        self.assertEqual(expected_new_mdi, mdi.to_json())


if __name__ == '__main__':
    unittest.main()
