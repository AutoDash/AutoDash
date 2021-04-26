#!/usr/bin/env python3
import unittest

from src.PipelineConfiguration import PipelineConfiguration
from src.executor.Barrier import Barrier
from src.data.MetaDataItem import MetaDataItem
from src.executor.iExecutor import iExecutor
from src.pipeline import run as administrator
from test.mock.MockDataAccessor import MockDataAccessor

class testCountExecutor(iExecutor):
    count = 0

class testExecutorSource(iExecutor):
    def run(self, ignore):
        items = []
        for i in range(5):
            items.append(MetaDataItem(title=None, url=None, download_src=None))
        return items

class testExecutorBeforeBarrier(testCountExecutor):
    def run(self, item):
        print("Before Barrier")
        testCountExecutor.count += 1
        return item

class testExecutorAfterBarrier(testCountExecutor):
    def run(self, item):
        print("After Barrier")
        assert(testCountExecutor.count == 5)
        return item

class TestExecutorFactory:
    @classmethod
    def build(cls, executor_name, parents=[]):
        local = {}
        exec(f'executor_class = {executor_name}', globals(), local)
        executor_class = local['executor_class']
        executor = executor_class(*parents)
        return executor


class TestBarrier(unittest.TestCase):

    def test_compiles(self):
        self.assertEqual(True, True)

    def test_stop_at_barrier(self):
        pc = PipelineConfiguration(ExecutorFactory=TestExecutorFactory)

        source = testExecutorSource()
        bef = testExecutorBeforeBarrier(source)
        bar = Barrier(bef)
        aft = testExecutorAfterBarrier(bar)

        pc.load_graph(aft)

        database = MockDataAccessor()

        administrator(pc, database, max_iterations=1)





if __name__ == '__main__':
    unittest.main()