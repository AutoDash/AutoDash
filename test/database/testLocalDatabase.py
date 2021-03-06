#!/usr/bin/env python3
import unittest

import os

from src.data.FilterCondition import FilterCondition
from src.data.MetaDataItem import MetaDataItem, gen_filename
from src.database.LocalStorageAccessor import LocalStorageAccessor
from src.utils import get_project_root


class TestLocalStorageAccessor(unittest.TestCase):

    def setUp(self):
        self.storage_loc = os.path.join(get_project_root(), "test_metadata_storage")
        self.storage = LocalStorageAccessor(self.storage_loc)

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_metadata_storage_dir_created(self):
        self.assertTrue(os.path.exists(self.storage_loc))

    def test_metadata_file_creation_and_deletion(self):
        metadata = MetaDataItem(title="title", url="fake url 1", download_src="youtube")
        try:
            self.storage.publish_new_metadata(metadata)
            self.assertTrue(metadata.id != "") # metadata id successfully updated by the publish call
            self.assertTrue(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata.id))))
        finally:
            self.storage.delete_metadata(metadata.id)
        self.assertFalse(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata.id))))

    def test_metadata_file_fetching(self):
        metadata = MetaDataItem(title="title", url="fake url 1", download_src="youtube")
        try:
            self.storage.publish_new_metadata(metadata)
            self.assertTrue(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata.id))))

            metadata2 = self.storage.fetch_metadata(metadata.id)
            self.assertEqual(str(metadata), str(metadata2))

        finally:
            self.storage.delete_metadata(metadata.id)
        # Ensure deletion worked so that data is not polluted
        self.assertFalse(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata.id))))

    def test_id_and_url_lists(self):
        metadata1 = MetaDataItem(title="title", url="fake url 1", download_src="youtube")
        metadata2 = MetaDataItem(title="title", url="fake url 2", download_src="youtube")
        try:
            self.storage.publish_new_metadata(metadata1)
            self.storage.publish_new_metadata(metadata2)

            actual_id_list = self.storage.fetch_video_id_list()
            self.assertEqual(actual_id_list, [metadata1.id, metadata2.id])

            actual_url_list = self.storage.fetch_video_url_list()
            self.assertEqual(actual_url_list, [metadata1.url, metadata2.url])

        # Clean up after test
        finally:
            self.storage.delete_metadata(metadata1.id)
            self.storage.delete_metadata(metadata2.id)
        self.assertFalse(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata1.id))))
        self.assertFalse(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata2.id))))

    def test_id_and_url_lists_generated_correctly_on_startup(self):
        metadata1 = MetaDataItem(title="title", url="fake url 1", download_src="youtube")
        metadata2 = MetaDataItem(title="title", url="fake url 2", download_src="youtube")
        try:
            self.storage.publish_new_metadata(metadata1)
            self.storage.publish_new_metadata(metadata2)

            # Create a second storage system to run the initialization code again with existing files
            storage2 = LocalStorageAccessor(self.storage_loc)

            actual_id_list = storage2.fetch_video_id_list()
            self.assertEqual(set(actual_id_list), {metadata1.id, metadata2.id})

            actual_url_list = storage2.fetch_video_url_list()
            self.assertEqual(set(actual_url_list), {metadata1.url, metadata2.url})

        # Clean up after test
        finally:
            self.storage.delete_metadata(metadata1.id)
            self.storage.delete_metadata(metadata2.id)
        self.assertFalse(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata1.id))))
        self.assertFalse(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata2.id))))

    def test_metadata_update(self):
        metadata = MetaDataItem(title="title", url="fake url 1", download_src="youtube")
        try:
            self.storage.publish_new_metadata(metadata)
            self.assertTrue(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata.id))))

            metadata.title = "new title"
            self.storage.update_metadata(metadata)
            # Ensure file is still there
            self.assertTrue(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata.id))))

            # Check that update was successful by fetching the file
            metadata = self.storage.fetch_metadata(metadata.id)
            self.assertEqual(metadata.title, "new title")

        finally:
            self.storage.delete_metadata(metadata.id)
        self.assertFalse(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata.id))))

    def test_filter_condition_query(self):
        metadata1 = MetaDataItem(title="title", url="fake url 1", download_src="youtube", collision_type="car", location="Canada")
        metadata2 = MetaDataItem(title="title", url="fake url 2", download_src="youtube", collision_type="human", location="Canada")
        metadata3 = MetaDataItem(title="title", url="fake url 3", download_src="youtube", collision_type="human", location="America")
        try:
            self.storage.publish_new_metadata(metadata1)
            self.storage.publish_new_metadata(metadata2)
            self.storage.publish_new_metadata(metadata3)

            condition = FilterCondition("title == 'title' and location == 'Canada' and collision_type != 'car'")
            print(condition.tokenize("title == 'title' and location == 'Canada' and collision_type != 'car'"))
            metadata_list = self.storage.fetch_newest_videos(filter_cond=condition)
            self.assertEqual(set(map(lambda metadata: metadata.url, metadata_list)), {metadata2.url})

        # Clean up after test
        finally:
            self.storage.delete_metadata(metadata1.id)
            self.storage.delete_metadata(metadata2.id)
            self.storage.delete_metadata(metadata3.id)
        self.assertFalse(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata1.id))))
        self.assertFalse(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata2.id))))
        self.assertFalse(os.path.exists(os.path.join(self.storage_loc, gen_filename(metadata3.id))))

if __name__ == '__main__':
    unittest.main()
