import os

class PipelineConfiguration:

    def __init__(self):
        raise NotImplementedError

    def _read_json(self, fpath):
        raise NotImplementedError

    def _read_yaml(self, fpath):
        raise NotImplementedError

    def _write_json(self, fpath):
        raise NotImplementedError

    def _write_yaml(self, fpath):
        raise NotImplementedError

    def _execute_rw(self, fpath, ffmt, rw_dict):
        if ffmt is None: _, ffmt=os.path.splitext(fpath)
        if ffmt.lower() not in rw_dict: raise ValueError(f"Invalid file format {ffmt.lower()}. Must be one of {rw_dict.keys()}")

        rw_dict[ffmt](fpath)

    def read(self, fpath, ffmt=None):
        self._execute_rw(fpath, ffmt, {
            'json' : self._read_json,
            'yml'  : self._read_yaml,
            'yaml' : self._read_yaml
        })
         
    def write(self, fpath, ffmt=None):
        self._execute_rw(fpath, ffmt, {
            'json' : self._write_json,
            'yml'  : self._write_yaml,
            'yaml' : self._write_yaml
        })

    def load_graph(self, input_nodes, sink_nodes):
        """ 
            Create PipelineConfiguration from existing graph

            :param input_nodes: list of PipelineNode objects that generate input to the pipeline - indegree 0
            :param sink_nodes:  list of PipelineNode objects that handle pipeline output - outdegree 0
        """

        # TODO: DFS / DAG verification
        raise NotImplementedError

