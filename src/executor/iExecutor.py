from abc import ABC, abstractmethod
from typing import Dict, Any


class iExecutor(ABC):
    def __init__(self, next: 'iExecutor'):
        self.next = next

    @abstractmethod
    def run(self, obj: Dict[str, Any]):
        pass
