from abc import ABC, abstractmethod
from typing import Dict, Any, List

class iExecutor(ABC):
    def __init__(self, prev: 'iExecutor' = None):
        self.prev = prev
        self.next = []
        if prev: prev.add_next(self)

    @abstractmethod
    def run(self, obj: Dict[str, Any]):
        pass

    def add_next(self, child):
        self.next.append(child)
    
    def set_prev(self, prev):
        self.prev = prev

    def get_name(self):
        return type(self).__name__
