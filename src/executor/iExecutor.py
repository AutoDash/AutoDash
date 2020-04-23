from abc import ABC, abstractmethod
from typing import Dict, Any, List


class iExecutor(ABC):
    def __init__(self, next: 'iExecutor', prev: List['iExecutor']):
        self.next = next
        self.prev = prev

    @abstractmethod
    def run(self, obj: Dict[str, Any]):
        pass
