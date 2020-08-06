from abc import ABC, abstractmethod
from ..data.VideoItem import VideoItem
from collections import Iterable


class iExecutor(ABC):
    def __init__(self, parents=None, stateful=False):
        if parents == None:
            parents = []
        self.stateful = stateful
        self.prev = parents if isinstance(parents, Iterable) else [parents]
        self.next = None
        for parent in self.prev:
            if parent:
                parent.set_next(self)

        super().__init__()

    @abstractmethod
    def run(self, item: VideoItem):
        pass

    def set_next(self, child):
        if self.next: raise RuntimeError("Executor already has child")
        self.next = child

    def add_prev(self, prev):
        self.prev.append(prev)

    def get_name(self):
        cls = self.__class__

        return cls.__module__ + '.' + cls.__name__

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

    def requires_database(self) -> bool:
        return False
