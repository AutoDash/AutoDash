#!/usr/bin/env python3
import unittest
import asyncio

from src.executor.YoutubeCrawler import YoutubeCrawler


class TestYouTubeCrawler(unittest.TestCase):
    def test_compiles(self):
        self.assertEqual(True, True)

    def test_crawl(self):
        async def __sub():
            crawler = YoutubeCrawler([], ["dashcam crash", "accident footage dashcam"], check_url=False)
            await crawler.next_downloadable()

        asyncio.run(__sub())

if __name__ == '__main__':
    unittest.main()
