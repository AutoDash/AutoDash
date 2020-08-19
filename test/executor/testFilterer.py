#!/usr/bin/env python3
import unittest

from src.signals import StopSignal
from src.executor.AutoLabeler import AutoLabeler
from src.data.MetaDataItem import MetaDataItem
from src.data.VideoItem import VideoItem
from src.executor.Filterer import Filterer


class TestFilterer(unittest.TestCase):

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_default_config(self):
        f = Filterer()

        m = MetaDataItem(id="Hello", title="hello", url="world", download_src="youtube")
        v = VideoItem(m)

        res_v = f.run(v)
        self.assertEqual(v, res_v)

        al = AutoLabeler()
        v = al.run(v)

        try:
            f.run(v)
            self.assertTrue(False)
        except StopSignal:
            #expected path
            pass