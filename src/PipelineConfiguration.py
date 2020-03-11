import os

"""
Usage:

    source = Source()

    youtube_dl = YoutubeDownloader(source)
    reddit_dl = RedditDownloader(source)
    imgur_dl = ImgurDownloader(source)

    ...

    admin = Administrator(youtube_dl, reddit_dl, imgur_dl)

    dashcam_filter = DashcamFilter(admin)
    accident_filter = AccidentFilter(admin)

    ...

    acceptor = Acceptor(dashcam_filter, accident_filter)

    ...

    sink = Sink(*generators)

    pipeline = PipelineConfiguration()
    pipeline.load_graph(input_nodes=[source], output_nodes=[sink])
    pipeline.run()
    pipeline.write("/my/path/myyml.yml")

"""


class PipelineNode:
    parents, children = [], []

    def __init__(self, *parents):
        self.parents = parents
        for parent in self.parents:
            parent._add_child(self)
            if self._input_type() != parent._output_type():
                raise ValueError()

    def _add_child(self, child):
        self.children.append(child)

    def _input_type(self):
        # return expected input type
        pass

    def _output_type(self):
        # return output type
        pass

    def __call__(self, *args, **kwargs):
        # run operation
        pass


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

    def load_graph(self, input_nodes, output_nodes):
        """ 
            Create PipelineConfiguration from existing graph

            :param input_nodes: list of PipelineNode objects that generate input to the pipeline - indegree 0
            :param output_nodes:  list of PipelineNode objects that handle pipeline output - outdegree 0
        """

        # TODO: DFS / DAG verification
        raise NotImplementedError

