from abc import ABC, abstractmethod
from typing import Dict, Any, List
from data.VideoItem import VideoItem


class iExecutor(ABC):
    def __init__(self, *parents, stateful=False):
        self.stateful = stateful
        self.prev = parents
        self.next = None
        for parent in parents:
            parent.set_next(self)


        self.database = None
        super().__init__()

    def set_database(self, database):
        self.database = database

    @abstractmethod
    def run(self, item: VideoItem):
        pass

    def set_next(self, child):
        if self.next: raise RuntimeError("Executor already has child")
        self.next = child

    def add_prev(self, prev):
        self.prev.append(prev)

    def get_name(self):
        return type(self).__name__

    def get_executor(self):
        return self

    def register_shared(self, manager):
        pass

    def shared(self, manager):
        return None

    def get_next(self):
        return self.next

    def set_lock(self, lock):
        self.lock = lock

    def get_lock(self):
        return self.lock

    def is_stateful(self):
        return self.stateful
