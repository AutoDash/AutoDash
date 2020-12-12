#!/usr/bin/env python3
from argparse import ArgumentParser, ArgumentTypeError
from multiprocessing import Process, managers

from .executor.iExecutor import iExecutor
from .PipelineConfiguration import PipelineConfiguration
from .database import get_database, DatabaseConfigOption
from .data.FilterCondition import FilterCondition
from .utils import get_project_root
from .signals import CancelSignal, StopSignal
from .database.DataUpdater import DataUpdater
from collections.abc import Iterable

import tensorflow as tf
import copy

database_arg_mapper = {
    'firebase': DatabaseConfigOption.firebase,
    'local': DatabaseConfigOption.local
}

# Needed for PyInstaller to work :(
from src.executor import AutoLabeler, CsvExporter, DeferTaskExecutor, ExecFilterer, FaceBlurrer, Filterer, FirebaseSource, FirebaseUpdater
from src.executor import Labeler, LocalStorageSource, LocalStorageUpdater, ObjectDetector, Printer, RedditCrawler, Splitter, UniversalDownloader
from src.executor import YoutubeCrawler, iDatabaseExecutor, uTaskCollector


class PipelineCLIParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument('--iterations',
                          type=PipelineCLIParser.positive_int_type,
                          default=10000,
                          help="Number of times to run pipeline loop",
                          dest='max_iterations')
        self.add_argument(
            '--mode',
            choices={'crawler', 'ucrawler', 'user'},
            default='user',
            help="Run mode. Either 'crawler', 'ucrawler', or 'user'")
        self.add_argument(
            '--storage',
            choices=database_arg_mapper,
            default='firebase',
            help="Data storage used. Either 'firebase' or 'local")
        self.add_argument(
            '--filter',
            type=str,
            help=
            'A relational condition over metadata that we pull, overrides any conditions set by executors'
        )
        self.add_argument('--config',
                          type=str,
                          default='default_configuration.yml',
                          dest='config')

    @staticmethod
    def positive_int_type(val):
        intval = int(val)
        if intval <= 0:
            raise ArgumentTypeError("%s is not a positive integer" % val)
        return intval


def main():
    args = {**vars(PipelineCLIParser().parse_args())}

    if not tf.test.is_gpu_available():
        print("WARNING: You are running tensorflow in CPU mode.")

    # Set up pipeline configuration
    config = PipelineConfiguration()
    config.read(f"{get_project_root()}/{args['config']}")
    run(config, **args)


def run(pipeline, **args):

    # Set up services
    source_executors, output_executor = pipeline.generate_graph()
    database = get_database(database_arg_mapper.get(args['storage'], None))
    dataUpdater = DataUpdater()
    dataUpdater.set_database(database)
    print(f"database: {database}")

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
        run_recur(executor, item, dataUpdater)


def run_recur(source_executor, item, dataUpdater):
    if not source_executor:
        print(f"finished execution chain\n\n")
        return
    print(f"Executing {source_executor}")
    try:
        items = source_executor.run(item)
        if items is None:
            return
    except StopSignal as e:
        print(f"Stopping Pipeline for metadataitem {item}\n\n\n reason: {e}")
        metadata = iExecutor.get_metadata(item)
        if metadata.tags['state'] == 'in-progress':
            metadata.add_tag('state', '')
        dataUpdater.safe_run(metadata)
        return
    except CancelSignal:
        metadata = iExecutor.get_metadata(item)
        metadata.is_cancelled = True
        metadata.add_tag('state', 'processed')
        dataUpdater.safe_run(metadata)
        return
    except RuntimeError as e:
        print(e)
        return

    if not isinstance(items, Iterable):
        items = [items]

    for next_item in items:
        metadata = iExecutor.get_metadata(next_item)
        if metadata.is_cancelled == True:
            metadata.add_tag('state', 'processed')
            dataUpdater.safe_run(metadata)
        else:
            run_recur(source_executor.get_next(), next_item, dataUpdater)


if __name__ == "__main__":
    main()
