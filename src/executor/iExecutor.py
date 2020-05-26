from abc import ABC, abstractmethod
from typing import Dict, Any


class iExecutor(ABC):

    def __init__(self, next: 'iExecutor'):
        self.next = next

        self.database = None
        super().__init__

    def set_database(self, database):
        self.database = database

    @abstractmethod
    def run(self, obj: Dict[str, Any]):
        pass
