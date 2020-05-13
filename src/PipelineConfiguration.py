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
    pipeline.load_graph(input_nodess=source)
    pipeline.run()
    pipeline.write("/my/path/myyml.yml")

"""

class ExecutorFactory:
    # TODO: this should probably be improved
    @classmethod
    def build(cls, executor_name, parents=[]):
        local = {}
        exec(f'executor_class = {executor_name}', globals(), local)
        executor_class = local['executor_class']
        executor = executor_class(*parents)
        return executor

class PipelineConfiguration:
    """
        Manages the executor pipeline. Only tree graphs are accepted.
    """

    def __init__(self, ExecutorFactory=ExecutorFactory):
        self.input_nodes = None
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

    def load_graph(self, input_nodes: List[iExecutor]):
        """ 
            Create PipelineConfiguration from existing graph. Stores graph in dict as: 

            [[layer_1], [layer_2], ... ]

            :param input_nodes: iExecutor object that generates input to the pipeline - indegree 0
        """

        if input_nodes is None: raise ValueError("Missing input.")
        if not isinstance(input_nodes, list): input_nodes = [input_nodes]
        if len(input_nodes) == 0: raise ValueError("Missing input nodes.")

        for inode in input_nodes:
            if inode.next != input_nodes[0].next:
                raise RuntimeError("All input executors must have the same child executor")

        self.input_nodes = input_nodes

        self.graph_dict = [[node.get_name() for node in input_nodes]]
        input_acceptor = input_nodes[0].next

        node = input_acceptor
        while(node):
            self.graph_dict.append([node.get_name()])
            node = node.next


    def generate_graph(self) -> [iExecutor, List[iExecutor]]:
        """
            Return a root executor and output executors from the loaded graph.

            :return [[input_executors], output_executor]
        """

        def traverse_and_generate(index=0, parents=[]):
            root_executor = [self.ExecutorFactory.build(executor_name=input_name, parents=parents) for input_name in self.graph_dict[index]]

            if index == len(self.graph_dict) - 1:
                if index == 0: return [root_executor, root_executor]
                return [root_executor[0], root_executor[0]]

            _, sink = traverse_and_generate(index+1, parents=root_executor)
            return [root_executor, sink]


        if self.graph_dict is None:
            raise RuntimeError("Graph not loaded.")

        if not isinstance(self.graph_dict[0], list):
            self.graph_dict[0] = [self.graph_dict[0]]

        return traverse_and_generate()
    
