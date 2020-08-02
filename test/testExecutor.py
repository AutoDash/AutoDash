#!/usr/bin/env python3
import unittest
from src.executor.Printer import Printer
from src.data.VideoItem import VideoItem


class TestIExecutor(unittest.TestCase):

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_printer(self):
        printer = Printer()
        printer.run(VideoItem(metadata=None, filepath=None))


if __name__ == '__main__':
    unittest.main()
