#!/usr/bin/env python3
import unittest

import asyncio

from src.crawler.iCrawler import iCrawler, UndefinedDatabaseException
from src.data.MetaDataItem import MetaDataItem
from test.mock.MockDataAccessor import MockDataAccessor


class MockCrawler(iCrawler):
    def __init__(self):
        super().__init__

    async def next_downloadable(self):
        return MetaDataItem("title", "fake url 1", "youtube", "car-v-car", "desc", "loc")

class TestICrawler(unittest.TestCase):

    def setUp(self):
        self.crawler = MockCrawler()
        self.database = MockDataAccessor()

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_no_database(self):
        metadata = asyncio.run(self.crawler.next_downloadable())

        try:
            asyncio.run(self.crawler.check_new_url(metadata.url))
            self.assertTrue(False)
        except UndefinedDatabaseException:
            # Expected error
            pass

        try:
            asyncio.run(self.crawler.publish_metadata(metadata))
            self.assertTrue(False)
        except UndefinedDatabaseException:
            # Expected error
            pass

    def test_check_new_url(self):
        self.crawler.set_database(self.database)

        metadata = asyncio.run(self.crawler.next_downloadable())
        self.assertTrue(asyncio.run(self.crawler.check_new_url(metadata.url)))

        asyncio.run(self.crawler.publish_metadata(metadata))
        self.assertFalse(asyncio.run(self.crawler.check_new_url(metadata.url)))

    def test_publish_metadata(self):
        self.crawler.set_database(self.database)

        metadata = asyncio.run(self.crawler.next_downloadable())
        asyncio.run(self.crawler.publish_metadata(metadata))

        fetched_metadata = asyncio.run(self.database.fetch_metadata(metadata.id))
        self.assertEqual(metadata.to_json(), fetched_metadata.to_json())

    def test_run(self):
        self.crawler.set_database(self.database)

        self.crawler.run({})

        id_list = asyncio.run(self.database.fetch_video_id_list())
        self.assertTrue(len(id_list) is 1)

        metadata = asyncio.run(self.database.fetch_metadata(id_list[0]))

        # Get exact copy of the metadata item that was published
        copy_metadata = asyncio.run(self.crawler.next_downloadable())

        self.assertEqual(metadata.to_json(), copy_metadata.to_json())


if __name__ == '__main__':
    unittest.main()
