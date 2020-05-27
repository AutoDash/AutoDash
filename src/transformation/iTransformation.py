from abc import ABC, abstractmethod
from typing import Dict, Any
from src.executor.iExecutor import iExecutor


class iTransformation(iExecutor):
    def run(self, obj: Dict[str, Any]):
        pass
