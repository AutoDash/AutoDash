#!/usr/bin/env python3
import unittest
from src.pipeline import run as administrator
from src.executor.iExecutor import iExecutor
from multiprocessing import Queue
from queue import Empty as EmptyException
from src.PipelineConfiguration import PipelineConfiguration

events = Queue()

class TestExecutor(iExecutor):
    def __init__(self, event_num, parents=[]):
        super().__init__(parents=parents)
        self.event_num = event_num

    def run(self, obj):
        print(f"run {self.event_num}")
        events.put(self.event_num)


class MultipleReturnExecutor(iExecutor):
    def __init__(self, iters, *parents):
        self.iters = iters
        super().__init__(parents)

    def run(self, obj):
        return [x for x in range(self.iters)]


class ExceptionExecutor(iExecutor):
    def __init__(self, *parents):
        super().__init__(parents)

    def run(self, obj):
        raise RuntimeError()


class TestAdministrator(unittest.TestCase):
    def test_main_single_process(self):
        num_items = 10

        pc = PipelineConfiguration()
        ptr = TestExecutor(0)

        for x in range(1, num_items):
            ptr = TestExecutor(x, ptr)

        pc.load_graph(ptr)

        administrator(pc, n_workers=1, max_iterations=1, storage='local')

        for i in range(num_items):
            self.assertEqual(events.get(timeout=2), i, "items in wrong order")

        self.assertRaises(EmptyException, events.get, True, 0.25)

    def test_main_multiple_returns_with_exceptions(self):
        num_items = 10

        pc = PipelineConfiguration()

        graph = MultipleReturnExecutor(num_items)
        TestExecutor(ExceptionExecutor(TestExecutor(1, graph)))

        pc.load_graph(graph)

        administrator(pc, n_workers=1, max_iterations=1, storage='local')

        for i in range(num_items):
            self.assertEqual(events.get(timeout=2), 1, "not enough items")

        self.assertRaises(EmptyException, events.get, True, 0.25)

    def test_main_multiple_returns(self):
        num_items = 10

        pc = PipelineConfiguration()

        graph = MultipleReturnExecutor(num_items)
        TestExecutor(1, graph)

        pc.load_graph(graph)

        administrator(pc, n_workers=1, max_iterations=1, storage='local')

        for i in range(num_items):
            self.assertEqual(events.get(timeout=2), 1, "not enough items")

        self.assertRaises(EmptyException, events.get, True, 0.25)

    def test_main_multi_process(self):
        num_items = 10

        pc = PipelineConfiguration()
        ptr = TestExecutor(0)

        for x in range(1, num_items):
            ptr = TestExecutor(x, ptr)

        pc.load_graph(ptr)

        administrator(pc, n_workers=2, max_iterations=3, storage='local')
        for i in range(num_items*3):
            events.get(timeout=2)

        self.assertRaises(EmptyException, events.get, True, 0.25)


if __name__ == '__main__':
    unittest.main()
