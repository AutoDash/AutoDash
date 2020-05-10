#!/usr/bin/env python3
import unittest

from src.data.MetaDataItem import MetaDataItem


class TestMetaDataItem(unittest.TestCase):

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_tag_overwrite(self):
        metadata =  MetaDataItem("", "title", "fake url 1", "youtube", "car-v-car", "desc", "loc")

        simple_tag = {
            "hello": "world",
            "number": 1
        }
        metadata.add_tag("simple", simple_tag)

        self.assertEqual(metadata.tags, {
            "simple": {
                "hello": "world",
                "number": 1
            }
        })

        updated_value_tag = {
            "number": 2
        }
        metadata.add_tag("simple", updated_value_tag)

        self.assertEqual(metadata.tags, {
            "simple": {
                "hello": "world",
                "number": 2
            }
        })


if __name__ == '__main__':
    unittest.main()
