#!/usr/bin/env python3
from multiprocessing.managers import BaseManager
from argparse import ArgumentParser, ArgumentTypeError
from multiprocessing import Process, JoinableQueue, managers
from src.executor.Printer import Printer


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
        self.add_argument('--source', type=str, required=True, help='HTTP link to firebase')
        self.add_argument('--filter', type=str, help='A relational condition over metadata that we pull')

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
                #work_queue.task_done()
                return
            print(f"Received work {work}")
            executor = work.executor
            item = work.item
            while executor is not None:
                print(executor)
                try:
                    item = executor.run(item)
                except RuntimeError as e:
                    print(e)
                    break
                executor = executor.get_next()
            print("Done processing work")
            #work_queue.task_done()


class StatefulExecutorProxy(managers.BaseProxy):
    def run(self, message):
        return self._callmethod('run', [message])

    def get_next(self):
        return self._callmethod('get_next')
    
    def set_lock(self, message):
        return self._callmethod('set_lock', [message])

class StatefulExecutorManager(managers.SyncManager):
    pass

def run(pipeline, **kwargs):
    num_workers = kwargs.get('n_workers', 1)

    source_executors, output_executor = pipeline.generate_graph()

    #work_queue = JoinableQueue(num_workers)
    work_queue = []

    context = {
        **kwargs,
        'work_queue': work_queue,
    }

    manager = StatefulExecutorManager()
    for executor in source_executors:
        if executor.stateful:
            executor.register_shared(manager)

    manager.start()
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

    # Start all workers
    for worker in workers:
        worker.start()

    print("signal complete")
    # A null job signals the end of work
    for _ in range(num_workers):
        work_queue.append(None)

    for worker in workers:
        worker.join()

    #work_queue.join()

def main():
    # TODO: build executors from file / command line arguments
    executor = Printer()
    run(executor)


if __name__ == "__main__":
    main()
