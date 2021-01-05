#!/usr/bin/env python3
import unittest

from src.data.MetaDataItem import MetaDataItem


class TestMetaDataItem(unittest.TestCase):
    def test_compiles(self):
        self.assertEqual(True, True)

    def test_tag_overwrite(self):
        metadata = MetaDataItem(title="title",
                                url="fake url 1",
                                download_src="youtube",
                                collision_type="car-v-car",
                                description="desc",
                                location="loc")

        simple_tag = {"hello": "world", "number": 1}
        metadata.add_tag("simple", simple_tag)

        self.assertEqual(metadata.tags,
                         {"simple": {
                             "hello": "world",
                             "number": 1
                         }})

        updated_value_tag = {"number": 2}
        metadata.add_tag("simple", updated_value_tag)

        self.assertEqual(metadata.tags,
                         {"simple": {
                             "hello": "world",
                             "number": 2
                         }})

    def test_from_json_accident_in_bbFields(self):
        json = {
            "id": "id",
            "title": "blah",
            "url": "www.ca",
            "download_src": "www.website.ca",
            "bb_fields": {
                "accident_locations": [1, 2, 3]
            },
        }
        mdi = MetaDataItem(**json)
        self.assertListEqual(mdi.bb_fields.collision_locations, [1, 2, 3])

    def test_from_json_accident_in_root(self):
        json = {
            "id": "id",
            "title": "blah",
            "url": "www.ca",
            "download_src": "www.website.ca",
            "accident_locations": [1, 2, 3]
        }
        mdi = MetaDataItem(**json)
        self.assertListEqual(mdi.bb_fields.collision_locations, [1, 2, 3])

    def test_from_json_accident_and_collision_in_root(self):
        json = {
            "id": "id",
            "title": "blah",
            "url": "www.ca",
            "download_src": "www.website.ca",
            "accident_locations": [2, 5, 7],
            "bb_fields": {
                "collision_locations": [1, 2, 3]
            },
        }
        mdi = MetaDataItem(**json)
        self.assertListEqual(mdi.bb_fields.collision_locations, [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
