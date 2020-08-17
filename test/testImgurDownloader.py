#!/usr/bin/env python3
import unittest, os
from src.downloader.ImgurDownloader import ImgurDownloader
from src.data.MetaDataItem import MetaDataItem


class TestImgurDownloader(unittest.TestCase):
    download_location = os.path.join(os.path.dirname(__file__), "test_data")

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_download_video(self):
        file_path = TestImgurDownloader.download_location
        downloader = ImgurDownloader(pathname=file_path)
        video_item = downloader.run(MetaDataItem(title="title",url="https://imgur.com/r/carcrash/tO6SNIo", download_src="imgur"))
        vid_filename = os.path.join(file_path,"httpsimgurcomrcarcrashtO6SNIo.mp4")
        self.assertTrue(os.path.exists(vid_filename))
        os.remove(vid_filename)

    def test_download_video_in_album(self):
        file_path = TestImgurDownloader.download_location
        downloader = ImgurDownloader(pathname=file_path)
        video_item = downloader.run(MetaDataItem(title="title",url="https://imgur.com/r/carcrash/EN6aTa6", download_src="imgur"))
        vid_filename = os.path.join(file_path,"httpsimgurcomrcarcrashEN6aTa6.mp4")
        self.assertTrue(os.path.exists(vid_filename))
        os.remove(vid_filename)


if __name__ == '__main__':
    unittest.main()
