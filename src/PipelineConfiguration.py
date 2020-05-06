import os
from src.executor.iExecutor import iExecutor
from typing import List
import json
import yaml
import pickle

"""
Usage:

    source = Source()
    youtube_dl = YoutubeDownloader(source)
    dashcam_filter = DashcamFilter(youtube_dl)
    accident_filter = AccidentFilter(dashcam_filter)
    sink = Sink(accident_filter)

    pipeline = PipelineConfiguration()
    pipeline.load_graph(input_nodes=source, output_nodes=[sink])
    pipeline.run()
    pipeline.write("/my/path/myyml.yml")

"""

class ExecutorFactory:
    # TODO: this should probably be improved
    @classmethod
    def build(cls, executor_name, parent=None):
        local = {}
        exec(f'executor_class = {executor_name}', globals(), local)
        executor_class = local['executor_class']
        executor = executor_class(parent)
        return executor

class PipelineConfiguration:
    """
        Manages the executor pipeline. Only tree graphs are accepted.
    """

    def __init__(self, ExecutorFactory=ExecutorFactory):
        self.input_node = None
        self.output_nodes = None
        self.graph_dict = None
        self.ExecutorFactory=ExecutorFactory

    def _read_pickle(self, fpath):
        with open(fpath, 'rb') as fin:
            data_dict = pickle.load(fin)
        self.__dict__.update(data_dict)

    def _write_pickle(self, fpath):
        with open(fpath, 'wb') as fout:
            pickle.dump(self.__dict__, fout, 2)

    def _read_json(self, fpath):
        with open(fpath, 'r') as fin:
            self.graph_dict = json.load(fin)

    def _read_yaml(self, fpath):
        with open(fpath, 'r') as fin:
            self.graph_dict = yaml.load(fin)

    def _write_json(self, fpath):
        with open(fpath, 'w') as fin:
            json.dump(self.graph_dict, fin)

    def _write_yaml(self, fpath):
        with open(fpath, 'w') as fin:
            yaml.dump(self.graph_dict, fin)

    def _execute_rw(self, fpath, ffmt, rw_dict):
        if ffmt is None: _, ffmt=os.path.splitext(fpath)
        ffmt = ffmt.strip('.')
        if ffmt.lower() not in rw_dict: raise ValueError(f"Invalid file format {ffmt.lower()}. Must be one of {rw_dict.keys()}")

        rw_dict[ffmt](fpath)

    def read(self, fpath, ffmt=None):
        self._execute_rw(fpath, ffmt, {
            'json' : self._read_json,
            'yml'  : self._read_yaml,
            'yaml' : self._read_yaml,
            'pkl'  : self._read_pickle
        })
         
    def write(self, fpath, ffmt=None):
        self._execute_rw(fpath, ffmt, {
            'json' : self._write_json,
            'yml'  : self._write_yaml,
            'yaml' : self._write_yaml,
            'pkl'  : self._write_pickle
        })

    def load_graph(self, input_node: iExecutor, output_nodes: List[iExecutor]):
        """ 
            Create PipelineConfiguration from existing graph. Stores graph in dict as: 

            {parent: [{childA: ...}, {childB: ...} ...]}

            :param input_node: iExecutor object that generates input to the pipeline - indegree 0
            :param output_nodes:  list of iExecutor objects that handle pipeline output - outdegree 0
        """

        def collect_nodes(root, visited):
            if root in visited: 
                raise RuntimeError("Graph must be a tree.")
            visited.add(root)
            root_graph = dict()
            root_graph[root.get_name()] = []
            for child in root.next:
                child_graph = collect_nodes(child, visited)
                root_graph[root.get_name()].append(child_graph)

            return root_graph

        if input_node is None or output_nodes is None: raise ValueError("Missing input.")
        if len(output_nodes) == 0: raise ValueError("Missing output nodes.")

        self.input_node = input_node
        self.output_nodes = output_nodes

        self.graph_dict = collect_nodes(input_node, set())

    def generate_graph(self) -> [iExecutor, List[iExecutor]]:
        """
            Return a root executor and output executors from the loaded graph.

            :return [input_executor, [output_executors]]
        """

        def traverse_and_generate(root_dict, visited, parent=None):
            root_name = list(root_dict.keys())[0]
            if root_name in visited: 
                raise RuntimeError("Graph must be a tree.")
            visited.add(root_name)
            
            root_executor = self.ExecutorFactory.build(executor_name=root_name, parent=parent)
            if len(root_dict[root_name]) == 0:
                return [root_executor, [root_executor]]

            sinks = []
            for child_dict in root_dict[root_name]:
                _, leaf_executors = traverse_and_generate(child_dict, visited=visited, parent=root_executor)
                sinks.extend(leaf_executors)

            return [root_executor, sinks]

        if self.graph_dict is None:
            raise RuntimeError("Graph not loaded.")

        return traverse_and_generate(self.graph_dict, set())
        
