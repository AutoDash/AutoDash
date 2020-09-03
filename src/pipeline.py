#!/usr/bin/env python3
from argparse import ArgumentParser, ArgumentTypeError
from multiprocessing import Process, managers
from .PipelineConfiguration import PipelineConfiguration
from .database import get_database, get_firebase_access, DatabaseConfigOption
from .data.FilterCondition import FilterCondition
from .signals import CancelSignal
from .utils import get_project_root
import tensorflow as tf
import copy

# Needed for PyInstaller to work :(
from src.executor import FirebaseSource, FaceBlurrer, Filterer, Labeler, LocalStorageSource, LocalStorageUpdater, ObjectDetector, Printer, RedditCrawler, UniversalDownloader, YoutubeCrawler

class PipelineCLIParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument('--iterations', type=PipelineCLIParser.positive_int_type, default=10000,
                help="Number of times to run pipeline loop", dest='max_iterations')
        self.add_argument('--mode', choices={'crawler', 'ucrawler', 'user'}, default='user',
                help="Run mode. Either 'crawler', 'ucrawler', or 'user'")
        self.add_argument('--storage', choices={'firebase', 'local'}, default='local',
                help="Data storage used. Either 'firebase' or 'local")
        self.add_argument('--filter', type=str, help='A relational condition over metadata that we pull, overrides any conditions set by executors')
        self.add_argument('--config', type=str, default='default_configuration.yml', dest='config')

    @staticmethod
    def positive_int_type(val):
        intval = int(val)
        if intval <= 0:
            raise ArgumentTypeError("%s is not a positive integer" % val)
        return intval

def main():
    args = { **vars(PipelineCLIParser().parse_args()) }
    
    if not tf.test.is_gpu_available():
        print("WARNING: You are running tensorflow in CPU mode.")    
    
    # Set up pipeline configuration
    config = PipelineConfiguration()
    config.read(f"{get_project_root()}/{args['config']}")
    run(config, **args)

def run(pipeline, **args):
    
    # Set up services
    parser = PipelineCLIParser()
    source_executors, output_executor = pipeline.generate_graph()
    database = get_database(args['storage'])

    for executor in source_executors:
        if executor.requires_database():
            executor.set_database(database)

    iterations = args['max_iterations']
    filter_str = args.get('filter')
    filter_cond = None
    if filter_str:
        filter_cond = FilterCondition(filter_str)

    for i in range(iterations):
        executor = source_executors[i % len(source_executors)]
        item = filter_cond
        try:
            while executor is not None:
                    item = executor.run(item)
                    executor = executor.get_next()
        except CancelSignal:
            item.is_cancelled = True
            get_firebase_access().update_metadata(item)
        except RuntimeError as e:
            print(e)


if __name__ == "__main__":
    main()
