import os
from .executor.iExecutor import iExecutor
from typing import List
import json
import yaml
import pickle
from collections import defaultdict


"""
Usage:

    pipeline = PipelineConfiguration()

    x = Source()
    x = YoutubeDownloader(x)
    x = DashcamFilter(x)
    x = AccidentFilter(x)
    x = Sink(x)

    pipeline.load_graph(x)

    administrator(pipeline, num_workers=4, ...)

    pipeline.write("/my/path/myyml.yml")

"""


class InvalidPipelineException(RuntimeError):
    '''Raise on invalid pipeline configuration file'''


def parse_list(dict, name, min_size=1):
    if name not in dict:
        raise InvalidPipelineException(f"Could not find {name}")

    obj = dict[name]

    if type(obj) not in [list, tuple]:
        raise InvalidPipelineException(f"{name} is not a list")
    if len(obj) < min_size:
        raise InvalidPipelineException(f"{name} must contain at more than {min_size-1} objects")

    return obj


class ConfigDict(yaml.YAMLObject):
    def __init__(self, dict):
        self.sources = parse_list(dict, 'dataSources')
        self.stages = parse_list(dict, 'processingStages')


class ExecutorFactory:
    # TODO: this should probably be improved
    @classmethod
    def build(cls, executor_name, args, parents=[]):
        local = {}
        res = executor_name.rsplit(".",1)
        exec(f'from src.executor.{executor_name} import {executor_name}', globals(), local)
        exec(f'executor_class = {executor_name}', globals(), local)
        executor_class = local['executor_class']
        executor = executor_class(parents, **args)
        return executor

class PipelineConfiguration:
    """
        Manages the executor pipeline. Only tree graphs are accepted.
    """

    def __init__(self, ExecutorFactory=ExecutorFactory):
        self.input_nodes = None
        self.output_node = None
        self.config_dict = None
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
            self.config_dict = ConfigDict(json.load(fin))

    def _read_yaml(self, fpath):
        with open(fpath, 'r') as fin:
            self.config_dict = ConfigDict(yaml.load(fin, Loader=yaml.FullLoader))

    def _write_json(self, fpath):
        with open(fpath, 'w') as fin:
            json.dump(self.config_dict, fin)

    def _write_yaml(self, fpath):
        with open(fpath, 'w') as fin:
            yaml.dump(self.config_dict, fin)

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

    def load_graph(self, output_node: iExecutor):
        """
            Create PipelineConfiguration from existing graph. Stores graph in dict as:

            [[layer_1], [layer_2], ... ]

            :param output_node: Final iExecutor object that is the output of the pipeline – outdegree 0
        """

        def get_input_nodes(leaf):
            queue = []
            graph_dict = []
            input_nodes = []

            queue.append((leaf, 0))
            cur_depth = -1
            while len(queue) > 0:
                node, depth = queue.pop(0)
                if depth > cur_depth:
                    cur_depth = depth

                if len(node.prev) == 0: input_nodes.append(node)

                for parent in node.prev:
                    queue.append((parent, depth+1))

            return input_nodes

        if output_node is None: raise ValueError("Missing input.")

        input_nodes = get_input_nodes(output_node)
        for inode in input_nodes:
            if inode.next != input_nodes[0].next:
                raise RuntimeError("All input executors must have the same child executor")

        self.input_nodes = input_nodes
        self.output_node = output_node


    def generate_graph(self) -> [iExecutor, List[iExecutor]]:
        """
            Return a root executor and output executors from the loaded graph.

            :return [[input_executors], output_executor]
        """

        def traverse_and_generate(index=0, parents=[]):
            if index >= len(self.config_dict.stages):
                return parents[0]

            node = self.config_dict.stages[index]
            root_executor = [self.ExecutorFactory.build(executor_name=node["executor"], args=node.get("config", {}), parents=parents)]

            return traverse_and_generate(index+1, parents=root_executor)

        if self.input_nodes and self.output_node:
            return self.input_nodes, self.output_node

        if self.config_dict is None:
            raise RuntimeError("Graph not loaded.")

        self.input_nodes = [self.ExecutorFactory.build(executor_name=node["executor"], args=node.get("config", {})) for node in self.config_dict.sources]
        self.output_node = traverse_and_generate(parents=self.input_nodes)

        print(f"input: {self.input_nodes}, output: {self.output_node}")

        return self.input_nodes, self.output_node
