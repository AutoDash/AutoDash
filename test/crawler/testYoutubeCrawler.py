#!/usr/bin/env python3
import unittest

from src.executor.YoutubeCrawler import YoutubeCrawler


class TestYouTubeCrawler(unittest.TestCase):
    def test_compiles(self):
        self.assertEqual(True, True)

    def test_crawl(self):
        def __sub():
            crawler = YoutubeCrawler([], ["dashcam crash", "accident footage dashcam"], check_url=False)
            crawler.next_downloadable()

        __sub()

if __name__ == '__main__':
    unittest.main()
