#!/usr/bin/env python3
from argparse import ArgumentParser, ArgumentTypeError
from multiprocessing import Process, managers

from .executor.iExecutor import iExecutor
from .PipelineConfiguration import PipelineConfiguration
from .database import get_database, DatabaseConfigOption
from .data.MetaDataItem import MetaDataItem
from .data.FilterCondition import FilterCondition
from .utils import get_project_root
from .signals import CancelSignal, StopSignal, SkipSignal, DeleteSignal, DriedSourceSignal
from .database.DataUpdater import DataUpdater
from collections.abc import Iterable

import copy
import signal, sys

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

    signal.signal(signal.SIGINT,
                  signal.default_int_handler)  #allow us to catch CTRL-C

    for i in range(iterations):
        if len(source_executors) == 0:
            break
        executor = source_executors[i % len(source_executors)]
        item = filter_cond
        try:
            process(executor, item, dataUpdater)
        except DriedSourceSignal:
            # source executor has specified that it will return no more data
            source_executors.pop(i % len(source_executors))


def submit_metadata(item, dataUpdater, reason):
    print(f"Stopping Pipeline for metadataitem {item}\n\n\n reason: {reason}")
    metadata = iExecutor.get_metadata(item)
    if metadata.tags.get('state') == 'in-progress':
        metadata.add_tag('state', '')
    dataUpdater.safe_run(metadata)


def process(source_executor, source_item, dataUpdater):
    work = [(source_executor, source_item)]
    while len(work) > 0:
        executor, item = work[-1]

        print(f"Executing {executor}")
        try:
            next_items = executor.run(item)
            if next_items is None:
                continue
        except StopSignal as e:
            submit_metadata(item, dataUpdater, e)
            continue
        except SkipSignal as e:
            print(
                f"Stopping Pipeline for metadataitem {item}\n\n\n reason: {e}")
            return
        except CancelSignal:
            cancel_item(iExecutor.get_metadata(item), dataUpdater)
            continue
        except DeleteSignal:
            metadata = iExecutor.get_metadata(item)
            dataUpdater.database.delete_metadata(metadata.id)
            continue
        except KeyboardInterrupt as e:
            submit_all_metadata(work, dataUpdater)
            raise e
        except RuntimeError as e:
            print(e)
            continue
        finally:
            work.pop()

        next_executor = executor.get_next()
        if next_executor is None:
            print("End of Execution Chain")
            continue

        if not isinstance(next_items, Iterable):
            next_items = [next_items]

        for next_item in reversed(next_items):
            metadata = iExecutor.get_metadata(next_item)
            if metadata.is_cancelled:
                cancel_item(metadata, dataUpdater)
            else:
                work.append((executor.get_next(), next_item))


def submit_all_metadata(work_queue, dataUpdater):
    for (_, item) in work_queue:
        submit_metadata(item, dataUpdater, "Program Quit")


def cancel_item(metadata: MetaDataItem, dataUpdater: DataUpdater):
    metadata.is_cancelled = True
    metadata.add_tag('state', 'processed')
    dataUpdater.safe_run(metadata)


if __name__ == "__main__":
    main()
