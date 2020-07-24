#!/usr/bin/env python3
import unittest

import asyncio

from src.data.MetaDataItem import MetaDataItem
from src.database.Source import Source
from test.mock.MockDataAccessor import MockDataAccessor

class TestSource(unittest.TestCase):

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_stateful(self):
        src = Source()

        mockdb = MockDataAccessor()
        asyncio.run(mockdb.publish_new_metadata(MetaDataItem("first", "fake url 1", "youtube")))
        asyncio.run(mockdb.publish_new_metadata(MetaDataItem("second", "fake url 2", "youtube")))
        src.set_database(mockdb)

        item = src.run()
        self.assertEqual("first", item.title)

        item = src.run()
        self.assertEqual("second", item.title)


if __name__ == '__main__':
    unittest.main()