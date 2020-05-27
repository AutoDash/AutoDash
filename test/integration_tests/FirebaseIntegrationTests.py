import unittest

import asyncio

from src.data.FilterCondition import FilterCondition
from src.data.MetaDataItem import MetaDataItem
from src.database.FirebaseAccessor import FirebaseAccessor
from src.database.iDatabase import NotExistingException

# These tests impact the production server and require modification access to said server,
#  therefore they should only be run locally and not automated while the database is being
#  observed by the runner of the tests. The effects on the database would be minimal, at most
#  just adding additional fake data, but that should still be avoided

class IntegrationTestFirebaseAccessor(unittest.TestCase):

    def setUp(self):
        self.storage = FirebaseAccessor()

    # Helper functions
    def metadata_exists(self, metadata: MetaDataItem) -> bool:
        try:
            asyncio.run(self.storage.fetch_metadata(metadata.id))
            return True
        except NotExistingException:
            return False

    def test_metadata_file_creation_and_deletion(self):
        metadata = MetaDataItem("title", "fake url 1", "youtube", "car-v-car", "desc", "loc")
        try:
            asyncio.run(self.storage.publish_new_metadata(metadata))
            self.assertTrue(metadata.id is not "")  # metadata id successfully updated by the publish call
            self.assertTrue(self.metadata_exists(metadata))
        finally:
            asyncio.run(self.storage.delete_metadata(metadata.id))
        self.assertFalse(self.metadata_exists(metadata))

    def test_metadata_file_fetching(self):
        metadata = MetaDataItem("title", "fake url 1", "youtube", "car-v-car", "desc", "loc")
        try:
            asyncio.run(self.storage.publish_new_metadata(metadata))
            self.assertTrue(self.metadata_exists(metadata))

            metadata2 = asyncio.run(self.storage.fetch_metadata(metadata.id))
            self.assertEqual(str(metadata), str(metadata2))

        finally:
            asyncio.run(self.storage.delete_metadata(metadata.id))
        # Ensure deletion worked so that data is not polluted
        self.assertFalse(self.metadata_exists(metadata))

    def test_id_and_url_lists(self):
        metadata1 = MetaDataItem("title", "fake url 1", "youtube", "car-v-car", "desc", "loc")
        metadata2 = MetaDataItem("title", "fake url 2", "youtube", "car-v-car", "desc", "loc")
        try:
            asyncio.run(self.storage.publish_new_metadata(metadata1))
            asyncio.run(self.storage.publish_new_metadata(metadata2))

            actual_id_list = asyncio.run(self.storage.fetch_video_id_list())
            self.assertTrue(all(map(lambda id: id in set(actual_id_list), {metadata1.id, metadata2.id})))

            actual_url_list = asyncio.run(self.storage.fetch_video_url_list())
            self.assertTrue(all(map(lambda id: id in set(actual_url_list), {metadata1.url, metadata2.url})))

        # Clean up after test
        finally:
            asyncio.run(self.storage.delete_metadata(metadata1.id))
            asyncio.run(self.storage.delete_metadata(metadata2.id))
        self.assertFalse(self.metadata_exists(metadata1))
        self.assertFalse(self.metadata_exists(metadata2))

    def test_second_accessor_does_not_initialize(self):
        self.assertTrue(FirebaseAccessor.initialized)

        # Creating a second firebase accessor shouldn't start the initialization code as that should only be run once
        # An error will be thrown if this initialization is run again
        storage2 = FirebaseAccessor()

    def test_metadata_update(self):
        metadata = MetaDataItem("title", "fake url 1", "youtube", "car-v-car", "desc", "loc")
        try:
            asyncio.run(self.storage.publish_new_metadata(metadata))
            self.assertTrue(self.metadata_exists(metadata))

            metadata.title = "new title"
            asyncio.run(self.storage.update_metadata(metadata))
            # Ensure file is still there
            self.assertTrue(self.metadata_exists(metadata))

            # Check that update was successful by fetching the file
            metadata = asyncio.run(self.storage.fetch_metadata(metadata.id))
            self.assertEqual(metadata.title, "new title")

        finally:
            asyncio.run(self.storage.delete_metadata(metadata.id))
        self.assertFalse(self.metadata_exists(metadata))

    def test_fetch_newest_videos(self):
        metadata1 = MetaDataItem("title", "fake url 1", "youtube", "car-v-car", "desc", "loc")
        metadata2 = MetaDataItem("title", "fake url 2", "youtube", "car-v-car", "desc", "loc")
        metadata3 = MetaDataItem("title", "fake url 3", "youtube", "car-v-car", "desc", "loc")

        try:
            asyncio.run(self.storage.publish_new_metadata(metadata1))
            asyncio.run(self.storage.publish_new_metadata(metadata2))
            asyncio.run(self.storage.publish_new_metadata(metadata3))
            self.assertTrue(self.metadata_exists(metadata1))
            self.assertTrue(self.metadata_exists(metadata2))
            self.assertTrue(self.metadata_exists(metadata3))

            metadata_list = asyncio.run(self.storage.fetch_newest_videos(metadata1.id))
            self.assertEqual(set(map(lambda metadata: metadata.url, metadata_list)), {metadata2.url, metadata3.url})

            metadata_list = asyncio.run(self.storage.fetch_newest_videos(metadata2.id))
            self.assertEqual(set(map(lambda metadata: metadata.url, metadata_list)), {metadata3.url})

            metadata_list = asyncio.run(self.storage.fetch_newest_videos(metadata3.id))
            self.assertEqual(metadata_list, [])

        finally:
            asyncio.run(self.storage.delete_metadata(metadata1.id))
            asyncio.run(self.storage.delete_metadata(metadata2.id))
            asyncio.run(self.storage.delete_metadata(metadata3.id))
        self.assertFalse(self.metadata_exists(metadata1))
        self.assertFalse(self.metadata_exists(metadata2))
        self.assertFalse(self.metadata_exists(metadata3))

    def test_fetch_metadata_with_tags(self):
        metadata = MetaDataItem("title", "fake url 1", "youtube", "car-v-car", "desc", "loc")
        metadata.add_tag("hello", "world")

        try:
            asyncio.run(self.storage.publish_new_metadata(metadata))

            fetched_metadata = asyncio.run(self.storage.fetch_metadata(metadata.id))
            self.assertEqual(fetched_metadata.to_json(), metadata.to_json())

        finally:
            asyncio.run(self.storage.delete_metadata(metadata.id))
        self.assertFalse(self.metadata_exists(metadata))

    def test_filter_condition_query(self):
        metadata1 = MetaDataItem("title", "fake url 1", "youtube", collision_type="car", location="Canada")
        metadata2 = MetaDataItem("title", "fake url 2", "youtube", collision_type="human", location="Canada")
        metadata3 = MetaDataItem("title", "fake url 3", "youtube", collision_type="human", location="America")

        try:
            asyncio.run(self.storage.publish_new_metadata(metadata1))
            asyncio.run(self.storage.publish_new_metadata(metadata2))
            asyncio.run(self.storage.publish_new_metadata(metadata3))
            self.assertTrue(self.metadata_exists(metadata1))
            self.assertTrue(self.metadata_exists(metadata2))
            self.assertTrue(self.metadata_exists(metadata3))

            condition = FilterCondition("title == 'title' and location == 'Canada' and collision_type != 'car'")
            metadata_list = asyncio.run(self.storage.fetch_newest_videos(filter_cond=condition))
            self.assertEqual(set(map(lambda metadata: metadata.url, metadata_list)), {metadata2.url})

        finally:
            asyncio.run(self.storage.delete_metadata(metadata1.id))
            asyncio.run(self.storage.delete_metadata(metadata2.id))
            asyncio.run(self.storage.delete_metadata(metadata3.id))
        self.assertFalse(self.metadata_exists(metadata1))
        self.assertFalse(self.metadata_exists(metadata2))
        self.assertFalse(self.metadata_exists(metadata3))
