from abc import ABC, abstractmethod
from src.data.VideoItem import VideoItem


class iExecutor(ABC):

    def __init__(self, *parents):
        self.prev = parents 
        self.next = None
        for parent in parents:
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
        return type(self).__name__
