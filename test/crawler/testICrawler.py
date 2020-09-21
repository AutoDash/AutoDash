#!/usr/bin/env python3
import unittest

from src.crawler.iCrawler import iCrawler, UndefinedDatabaseException
from src.data.MetaDataItem import MetaDataItem
from test.mock.MockDataAccessor import MockDataAccessor


class MockCrawler(iCrawler):
    def __init__(self):
        super().__init__()

    def next_downloadable(self):
        return MetaDataItem(
                title="title", 
                url="fake url 1", 
                download_src="youtube") 

class TestICrawler(unittest.TestCase):

    def setUp(self):
        self.crawler = MockCrawler()
        self.database = MockDataAccessor()

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_no_database(self):
        metadata = self.crawler.next_downloadable()

        try:
            self.crawler.check_new_url(metadata.url)
            self.assertTrue(False)
        except UndefinedDatabaseException:
            # Expected error
            pass

    def test_check_new_url(self):
        self.crawler.set_database(self.database)

        metadata = self.crawler.next_downloadable()
        self.assertTrue(self.crawler.check_new_url(metadata.url))

        self.database.publish_new_metadata(metadata)
        self.assertFalse(self.crawler.check_new_url(metadata.url))

    def test_run(self):
        self.crawler.set_database(self.database)

        metadata = self.crawler.run({})
        self.database.publish_new_metadata(metadata)

        id_list = self.database.fetch_video_id_list()
        self.assertTrue(len(id_list) == 1)

        metadata = self.database.fetch_metadata(id_list[0])

        # Get exact copy of the metadata item that was published
        copy_metadata = self.crawler.next_downloadable()

        self.assertEqual(metadata.to_json(), copy_metadata.to_json())


if __name__ == '__main__':
    unittest.main()
