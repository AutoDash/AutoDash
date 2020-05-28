#!/usr/bin/env python3
import unittest, os
from src.StorageService import StorageService
from src.data.VideoItem import VideoItem
from src.data.MetaDataItem import MetaDataItem

class TestUnitTest(unittest.TestCase):
    def setUp(self):
        self.storage = StorageService()

    def test_storage_file_created(self):
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), "storage")))

    def test_store_load_delete_video(self):
        metaData = MetaDataItem("title","url","youtube","car-v-car","desc","loc")
        vidItem = VideoItem(metadata=metaData)

        self.storage.store_video(vidItem)
        self.assertTrue(os.path.exists(self.storage.get_file(vidItem)))

        vidItem2 = self.storage.load_video(metaData)
        self.assertEqual(vidItem.encode(), vidItem2.encode())

        self.storage.delete_video(vidItem)
        self.assertFalse(os.path.exists(self.storage.get_file(vidItem)))

    def test_list_and_delete_all(self):
        videos = ["vid1", "vid2", "vid3"]

        for vid in videos:
            self.storage.store_video(
                VideoItem(metadata=MetaDataItem(
                        "title",vid,"youtube","comp","desc","loc"
                    )
                )
            )

        for vid in self.storage.list_videos():
            videos.remove(vid.metadata.url)

        self.assertTrue(len(videos) == 0, "Not all videos listed")

        self.storage.delete_all()
        self.assertTrue(
            len([x for x in self.storage.list_videos()]) == 0,
            "Not all videos deleted"
        )

    def test_delete_all(self):
        pass

if __name__ == '__main__':
    unittest.main()
