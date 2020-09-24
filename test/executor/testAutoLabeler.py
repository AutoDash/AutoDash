#!/usr/bin/env python3
import unittest

from src.signals import StopSignal
from src.executor.AutoLabeler import AutoLabeler
from src.data.MetaDataItem import MetaDataItem
from src.data.VideoItem import VideoItem
from src.executor.Filterer import Filterer


class TestAutoLabeler(unittest.TestCase):

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_update_state(self):

        m = MetaDataItem(id="Hello", title="hello", url="world", download_src="youtube")
        v = VideoItem(m)


        al_prog = AutoLabeler(val="in-progress")
        v = al_prog.run(v)

        self.assertEqual(v.metadata.get_tag('state'), "in-progress")

        al_comp = AutoLabeler()
        v = al_comp.run(v)

        self.assertEqual(v.metadata.get_tag('state'), "processed")