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
    def build(cls, executor_name, parents=[]):
        local = {}
        exec(f'executor_class = {executor_name}', globals(), local)
        executor_class = local['executor_class']
        executor = executor_class(*parents)
        return executor

class TestUnitTest(unittest.TestCase):
    
    def test_read_write_invalid_format(self):
        pc = PipelineConfiguration(ExecutorFactory=TestExecutorFactory)
        exA = testExecutorA()

        pc.load_graph(exA)

        self.assertRaises(ValueError, PipelineConfiguration.write, pc, 'out.mov')
        self.assertRaises(ValueError, PipelineConfiguration.read, pc, 'out.mov')

    def test_load_null_graph(self):
        pc = PipelineConfiguration()
        self.assertRaises(ValueError, PipelineConfiguration.load_graph, pc, None)

    def test_generate_without_load(self):
        pc = PipelineConfiguration()
        self.assertRaises(RuntimeError, PipelineConfiguration.generate_graph, pc)

    def test_single_node_graph(self):
        pc = PipelineConfiguration(ExecutorFactory=TestExecutorFactory)
        ex = testExecutorA()
        pc.load_graph(ex)
        roots, sink = pc.generate_graph()
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].get_name(), ex.get_name())
        self.assertEqual(sink[0].get_name(), ex.get_name())

    def test_only_input_node_graph(self):
        pc = PipelineConfiguration(ExecutorFactory=TestExecutorFactory)
        exA = testExecutorA()
        exB = testExecutorB()
        pc.load_graph([exA, exB])
        roots, sink = pc.generate_graph()
        self.assertEqual(len(roots), 2)
        self.assertEqual(roots[0].get_name(), exA.get_name())
        self.assertEqual(roots[1].get_name(), exB.get_name())
        self.assertEqual(sink[0].get_name(), exA.get_name())
        self.assertEqual(sink[1].get_name(), exB.get_name())

    def test_linear_graph(self):
        pc = PipelineConfiguration(ExecutorFactory=TestExecutorFactory)
        exA = testExecutorA()
        exB = testExecutorB(exA)
        exC = testExecutorC(exB)
        exD = testExecutorD(exC)

        pc.load_graph([exA])
        roots, sink = pc.generate_graph()

        self.assertEqual(len(roots), 1)

        res_exA = roots[0]
        self.assertEqual(res_exA.get_name(), exA.get_name())

        res_exB = res_exA.next
        self.assertEqual(res_exB.get_name(), exB.get_name())

        res_exC = res_exB.next
        self.assertEqual(res_exC.get_name(), exC.get_name())

        res_exD = res_exC.next
        self.assertEqual(res_exD.get_name(), exD.get_name())

        self.assertEqual(sink.get_name(), exD.get_name())

    def test_simple_tree(self):
        exA = testExecutorA()
        exB = testExecutorB(exA)
        exC = testExecutorC(exB)
        self.assertRaises(RuntimeError, testExecutorD, exA)

    def test_multiple_valid_input_nodes(self):
        pc = PipelineConfiguration(ExecutorFactory=TestExecutorFactory)

        exA = testExecutorA()
        exB = testExecutorB()
        exC = testExecutorC(exA, exB)
        exD = testExecutorD(exC)

        pc.load_graph([exA, exB])
        roots, sink = pc.generate_graph()

        self.assertEqual(len(roots), 2)
        
        res_exA, res_exB = roots

        self.assertEqual(res_exA.get_name(), exA.get_name())
        self.assertEqual(res_exB.get_name(), exB.get_name())

        res_exC_A = res_exA.next
        res_exC_B = res_exB.next

        self.assertEqual(res_exC_A.get_name(), res_exC_B.get_name())
        self.assertEqual(exC.get_name(), res_exC_A.get_name())

        res_exD_A = res_exC_A.next
        res_exD_B = res_exC_B.next

        self.assertEqual(res_exD_A.get_name(), res_exD_B.get_name())
        self.assertEqual(exD.get_name(), res_exD_A.get_name())


    def test_multiple_invalid_input_nodes(self):
        pc = PipelineConfiguration(ExecutorFactory=TestExecutorFactory)

        exA = testExecutorA()
        exB = testExecutorB(exA)
        exD = testExecutorD()
        exC = testExecutorC(exB, exD)

        self.assertRaises(RuntimeError, pc.load_graph, [exA, exD])


if __name__ == '__main__':
    unittest.main(buffer=True)
