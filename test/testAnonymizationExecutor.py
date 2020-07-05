#!/usr/bin/env python3
import unittest
import os
import shutil
from src.executor.FaceBlurrer import FaceBlurrer
from src.StorageService import StorageService
from numpy.testing import assert_array_equal, assert_raises

class TestAnonymizationExecutor(unittest.TestCase):
    TEST_DIR = os.path.join(os.getcwd(), "anontest")
    TEST_FILE = "test.mp4"
    TEST_FILE_PATH = os.path.join(TEST_DIR, TEST_FILE)

    def setUp(self):
        self.storage = StorageService()
        # Create test directory and copy one of the test videos from the anonymization repo into it
        os.mkdir(self.TEST_DIR)
        shutil.copy2(os.path.join(os.getcwd(), "lib/anonymization/dataset/input/man_face.mp4"), self.TEST_FILE_PATH)
        self.video = self.storage.load_file(self.TEST_FILE_PATH)

    def tearDown(self):
        # Delete test directory
        os.rmdir(self.TEST_DIR)

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_video_creation(self):
        original_data = self.video.npy

        # Running the face blurrer should overwrite the input file
        face_blurrer = FaceBlurrer()
        new_data = face_blurrer.run(self.video)

        # Now we check that the video data has changed
        assert_raises(AssertionError, assert_array_equal, original_data, new_data)

if __name__ == '__main__':
    unittest.main()
