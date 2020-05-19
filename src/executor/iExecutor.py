from abc import ABC, abstractmethod
from src.data.VideoItem import VideoItem


class iExecutor(ABC):
    def __init__(self, next: 'iExecutor'):
        self.next = next

    @abstractmethod
    def run(self, obj : Dict[str, Any]):
        pass
