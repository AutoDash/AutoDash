#!/usr/bin/env python3
import unittest
from src.pipeline import run as administrator
from src.pipeline import process
from src.executor.iExecutor import iExecutor
from multiprocessing import Queue
from queue import Empty as EmptyException
from src.PipelineConfiguration import PipelineConfiguration
from src.data.MetaDataItem import MetaDataItem
import pytest
from unittest.mock import MagicMock

events = Queue()


class TestExecutor(iExecutor):
    def __init__(self, event_num, parents=[]):
        super().__init__(parents=parents)
        self.event_num = event_num

    def run(self, obj):
        print(f"run {self.event_num}")
        events.put(self.event_num)
        return MetaDataItem(title=None, url=None, download_src=None)


class MultipleReturnExecutor(iExecutor):
    def __init__(self, iters, *parents):
        self.iters = iters
        super().__init__(parents)

    def run(self, obj):
        return [
            MetaDataItem(title=None, url=None, download_src=None)
            for _ in range(self.iters)
        ]


class ExceptionExecutor(iExecutor):
    def __init__(self, *parents):
        super().__init__(parents)

    def run(self, obj):
        raise RuntimeError()


def test_main_single_process():
    num_items = 10

    pc = PipelineConfiguration()
    ptr = TestExecutor(0)

    for x in range(1, num_items):
        ptr = TestExecutor(x, ptr)

    pc.load_graph(ptr)

    administrator(pc, n_workers=1, max_iterations=1, storage='local')

    for i in range(num_items):
        assert events.get(timeout=2) == i, "items in wrong order"

    with pytest.raises(EmptyException):
        events.get(True, 0.25)


def test_main_multiple_returns_with_exceptions():
    num_items = 10

    pc = PipelineConfiguration()

    graph = MultipleReturnExecutor(num_items)
    TestExecutor(ExceptionExecutor(TestExecutor(1, graph)))

    pc.load_graph(graph)

    administrator(pc, n_workers=1, max_iterations=1, storage='local')

    for i in range(num_items):
        assert events.get(timeout=2) == 1, "not enough items"

    with pytest.raises(EmptyException):
        events.get(True, 0.25)


def test_main_multiple_returns():
    num_items = 10

    pc = PipelineConfiguration()

    graph = MultipleReturnExecutor(num_items)
    TestExecutor(1, graph)

    pc.load_graph(graph)

    administrator(pc, n_workers=1, max_iterations=1, storage='local')

    for i in range(num_items):
        assert events.get(timeout=2) == 1, "not enough items"

    with pytest.raises(EmptyException):
        events.get(True, 0.25)


def test_main_multi_process():

    num_items = 10

    pc = PipelineConfiguration()
    ptr = TestExecutor(0)

    for x in range(1, num_items):
        ptr = TestExecutor(x, ptr)

    pc.load_graph(ptr)

    administrator(pc, max_iterations=3, storage='local')
    for i in range(num_items * 3):
        events.get(timeout=2)

    with pytest.raises(EmptyException):
        events.get(True, 0.25)


def test_ctrl_c():
    def raise_ki(self):
        raise KeyboardInterrupt

    parent = MultipleReturnExecutor(3)

    child = MultipleReturnExecutor(1, parent)
    child.run = raise_ki
    parent.next = child

    mock_data_updater = MagicMock()

    with pytest.raises(KeyboardInterrupt):
        process(parent, None, mock_data_updater)
        assert mock_data_updater.call_count == 2


if __name__ == '__main__':
    unittest.main()
