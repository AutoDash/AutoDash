#!/usr/bin/env python3
from argparse import ArgumentParser, ArgumentTypeError
from multiprocessing import Process, JoinableQueue
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
    def __init__(self, context, name, *args, **kwargs):
        super().__init__(*args, name=name, **kwargs)
        self.context = context

    def run(self):
        print(f'Worker {self.name} is running')
        work_queue = self.context['work_queue']
        while True:
            work = work_queue.get()
            if work is None:
                print("done")
                work_queue.task_done()
                return
            print(f"Received work {work}")
            executor = work.executor
            item = work.item
            while executor is not None:
                executor.run(item)
                executor = executor.next
            print("Done processing work")
            work_queue.task_done()


def run(executors, **kwargs):
    num_workers = kwargs.get('n_workers', 1)
    work_queue = JoinableQueue(num_workers)

    context = {
        **kwargs,
        'work_queue': work_queue,
    }

    workers = [
        PipelineWorker(context, name=f"worker-{i}")
        for i in range(0, num_workers)
    ]

    # Start all workers
    for worker in workers:
        worker.start()

    iterations = context.get('max_iterations', 10000)

    for i in range(iterations):
        print("put work")
        work_queue.put(Work(executors[i % len(executors)], None))

    print("signal complete")
    # A null job signals the end of work
    for _ in range(num_workers):
        work_queue.put(None)

    work_queue.join()


def main():
    # TODO: build executors from file / command line arguments
    executor = Printer()
    run(executor)



def main():
    # TODO: build executors from file / command line arguments
    executor = Printer()
    run(executor)


if __name__ == "__main__":
    main()
