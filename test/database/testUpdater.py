#!/usr/bin/env python3
import unittest

from src.signals import StopSignal
from src.data.MetaDataItem import MetaDataItem
from src.database.DataUpdater import DataUpdater
from test.mock.MockDataAccessor import MockDataAccessor

class TestUpdater(unittest.TestCase):

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_unique_urls(self):
        upd = DataUpdater()

        mockdb = MockDataAccessor()
        upd.set_database(mockdb)

        upd.run(MetaDataItem(title="unique", url="fake url 1", download_src="youtube"))
        upd.run(MetaDataItem(title="repeat1", url="fake url 2", download_src="youtube", is_split_url=True))

        try:
            upd.run(MetaDataItem(title="not allowed", url="fake url 1", download_src="youtube"))
            self.assertTrue(False)
        except StopSignal:
            # expected path
            pass

        upd.run(MetaDataItem(title="repeat2", url="fake url 2", download_src="youtube", is_split_url=True))


if __name__ == '__main__':
    unittest.main()