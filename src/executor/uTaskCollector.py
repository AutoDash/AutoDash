from .iExecutor import iExecutor

class uTaskCollector(iExecutor):
    def __init__(self, *parents):
        super().__init__(*parents)

    def run(self, item):
        return item
