from abc import ABC, abstractmethod
from typing import Dict, Any

class iExecutor(ABC):
    @abstractmethod
    def run(obj : Dict[str, Any]):
        pass
