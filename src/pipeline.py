#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentTypeError
from multiprocessing import Process, Pool, Queue
from socket import gethostname

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
                return
            print(f"Received work {work}")

def main():
    parser = PipelineCLIParser(description='AutoDash pipeline for processing (near-)accident dashcam footage')
    args = parser.parse_args()

    hostname = gethostname()
    context = { 
        **vars(args), 
        'work_queue': Queue(),
        'hostname': hostname
    }

    workers = [
        PipelineWorker(context, name=f"worker-{hostname}-{i}")
        for i in range(0, context['n_workers'])
    ]

    # Start all workers
    for worker in workers:
        worker.start()

    # A null job signals the end of work
    for _ in range(0, context['n_workers']):
        context['work_queue'].put(None)

if __name__ == "__main__":
    main()
