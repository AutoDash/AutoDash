import unittest

from src.executor.YoutubeCrawler import YoutubeCrawler

class IntegrationTestYoutubeCrawler(unittest.TestCase):

    def test_crawl(self):
        def __sub():
            crawler = YoutubeCrawler([], ["dashcam crash", "accident footage dashcam"], check_url=False)
            crawler.next_downloadable()

        __sub()