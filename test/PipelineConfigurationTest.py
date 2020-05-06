#!/usr/bin/env python3
import unittest
from src.PipelineConfiguration import PipelineConfiguration
from src.executor.iExecutor import iExecutor

class testExecutorA(iExecutor):
    def run(self):
        pass

class testExecutorB(iExecutor):
    def run(self):
        pass

class testExecutorC(iExecutor):
    def run(self):
        pass

class testExecutorD(iExecutor):
    def run(self):
        pass


class TestExecutorFactory:
    @classmethod
    def build(cls, executor_name, parent=None):
        local = {}
        exec(f'executor_class = {executor_name}', globals(), local)
        executor_class = local['executor_class']
        executor = executor_class(parent)
        return executor

class TestUnitTest(unittest.TestCase):
    
    def test_read_write_invalid_format(self):
        pc = PipelineConfiguration(ExecutorFactory=TestExecutorFactory)
        exA = testExecutorA()

        pc.load_graph(exA, [exA])

        self.assertRaises(ValueError, PipelineConfiguration.write, pc, 'out.mov')
        self.assertRaises(ValueError, PipelineConfiguration.read, pc, 'out.mov')

    def test_load_null_graph(self):
        pc = PipelineConfiguration()
        self.assertRaises(ValueError, PipelineConfiguration.load_graph, pc, None, None)

    def test_generate_without_load(self):
        pc = PipelineConfiguration()
        self.assertRaises(RuntimeError, PipelineConfiguration.generate_graph, pc)

    def test_single_node_graph(self):
        pc = PipelineConfiguration(ExecutorFactory=TestExecutorFactory)
        ex = testExecutorA()
        pc.load_graph(ex, [ex])
        root, sinks = pc.generate_graph()
        self.assertEqual(root.get_name(), ex.get_name())
        self.assertEqual(len(sinks), 1)
        self.assertEqual(sinks[0].get_name(), ex.get_name())

    def test_linear_graph(self):
        pc = PipelineConfiguration(ExecutorFactory=TestExecutorFactory)
        exA = testExecutorA()
        exB = testExecutorB(exA)
        exC = testExecutorC(exB)
        exD = testExecutorD(exC)

        pc.load_graph(exA, [exD])
        root, sinks = pc.generate_graph()

        res_exA = root
        self.assertEqual(res_exA.get_name(), exA.get_name())
        self.assertEqual(len(res_exA.next), 1)

        res_exB = res_exA.next[0]
        self.assertEqual(res_exB.get_name(), exB.get_name())
        self.assertEqual(len(res_exB.next), 1)

        res_exC = res_exB.next[0]
        self.assertEqual(res_exC.get_name(), exC.get_name())
        self.assertEqual(len(res_exC.next), 1)

        res_exD = res_exC.next[0]
        self.assertEqual(res_exD.get_name(), exD.get_name())
        self.assertEqual(len(res_exD.next), 0)

        self.assertEqual(len(sinks), 1)
        self.assertEqual(sinks[0].get_name(), exD.get_name())

    def test_simple_tree(self):
        pc = PipelineConfiguration(ExecutorFactory=TestExecutorFactory)
        exA = testExecutorA()
        exB = testExecutorB(exA)
        exC = testExecutorC(exB)
        exD = testExecutorD(exA)

        pc.load_graph(exA, [exC, exD])
        root, sinks = pc.generate_graph()

        res_exA = root
        self.assertEqual(res_exA.get_name(), exA.get_name())
        self.assertEqual(len(res_exA.next), 2)

        res_exB = res_exA.next[0]
        self.assertEqual(res_exB.get_name(), exB.get_name())
        self.assertEqual(len(res_exB.next), 1)

        res_exC = res_exB.next[0]
        self.assertEqual(res_exC.get_name(), exC.get_name())
        self.assertEqual(len(res_exC.next), 0)

        res_exD = res_exA.next[1]
        self.assertEqual(res_exD.get_name(), exD.get_name())
        self.assertEqual(len(res_exD.next), 0)

        self.assertEqual(len(sinks), 2)
        self.assertEqual(sinks[0].get_name(), exC.get_name())
        self.assertEqual(sinks[1].get_name(), exD.get_name())

if __name__ == '__main__':
    unittest.main(buffer=True)
