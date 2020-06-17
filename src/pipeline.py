#!/usr/bin/env python3
from multiprocessing.managers import BaseManager
from argparse import ArgumentParser, ArgumentTypeError
<<<<<<< HEAD
from multiprocessing import Process, JoinableQueue, managers
from src.executor.Printer import Printer
=======
from multiprocessing import Process, JoinableQueue
from PipelineConfiguration import PipelineConfiguration
from executor.Printer import Printer
>>>>>>> tie configuration and pipeline together


class Work:
    def __init__(self, executor, item):
        self.executor = executor
        self.item = item


class PipelineCLIParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument('--workers', type=PipelineCLIParser.positive_int_type, default=1,
                help="Number of workers to process work", dest='n_workers')
        self.add_argument('--mode', choices={'crawler', 'ucrawler', 'user'}, default='user',
                help="Run mode. Either 'crawler', 'ucrawler', or 'user'")
        self.add_argument('--storage', choices={'firebase', 'local'}, default='local',
                help="Data storage used. Either 'firebase' or 'local")
        self.add_argument('--filter', type=str, help='A relational condition over metadata that we pull')
        self.add_argument('--config', type=str, dest='config')

    @staticmethod
    def positive_int_type(val):
        intval = int(val)
        if intval <= 0:
            raise ArgumentTypeError("%s is not a positive integer" % val)
        return intval


class PipelineWorker(Process):
    def __init__(self, context, name, queue_lock, *args, **kwargs):
        super().__init__(*args, name=name, **kwargs)
        self.context = context
        self.lock = queue_lock

    def run(self):
        work_queue = self.context['work_queue']
        print("worker: ", self)
        while True:
            with self.lock:
                if len(work_queue) == 0: return
                work = work_queue.pop(0)
            if work is None:
                print("done")
                return
            print(f"Received work {work}")
            executor = work.executor
            item = work.item
            while executor is not None:
                try:
                    if executor.is_stateful():
                        with executor.get_lock():
                            item = executor.run(item)
                    else:
                        item = executor.run(item)
                except RuntimeError as e:
                    print(e)
                    break
                executor = executor.get_next()
            print("Done processing work")


class StatefulExecutorProxy(managers.BaseProxy):
    def run(self, message):
        return self._callmethod('run', [message])

    def get_next(self):
        return self._callmethod('get_next')
    
    def set_lock(self, message):
        return self._callmethod('set_lock', [message])

    def get_lock(self):
        return self._callmethod('get_lock')

    def is_stateful(self):
        return self._callmethod('is_stateful')

class StatefulExecutorManager(managers.SyncManager):
    def register_executor(self, name, executor):
        self.register(
                name, lambda: executor, 
                proxytype=StatefulExecutorProxy, 
                exposed=['run', 'get_next', 'set_lock', 'get_lock', 'is_stateful']
        )

def run(pipeline, **kwargs):
    num_workers = kwargs.get('n_workers', 1)

    source_executors, output_executor = pipeline.generate_graph()

    manager = StatefulExecutorManager()
    
    for executor in source_executors:
        if executor.is_stateful():
            executor.register_shared(manager)

    manager.start()

    work_queue = manager.list()
    context = {
        **kwargs,
        'work_queue': work_queue,
    }
    queue_lock = manager.Lock()
    workers = [
        PipelineWorker(context, name=f"worker-{i}", queue_lock=queue_lock)
        for i in range(0, num_workers)
    ]

    iterations = context.get('max_iterations', 10000)

    for i in range(iterations):
        print("put work")
        executor = source_executors[i % len(source_executors)]
        work_executor = executor.share(manager) if executor.stateful else executor
        work_executor.set_lock(manager.Lock())
        work_queue.append(Work(work_executor, None))

    print("signal complete")

    # A null job signals the end of work
    for _ in range(num_workers):
        work_queue.append(None)

    # Start all workers
    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()


def main():
    config = PipelineConfiguration()
    parser = PipelineCLIParser()
    args = parser.parse_args()

    print(args)
    if args.config is None:
        config.load_graph(Printer())  # TODO: load default config from a file
    else:
        config.read(args.config)

    run(config, **vars(args))


if __name__ == "__main__":
    main()
