from executor.iExecutor import iExecutor


class Printer(iExecutor):
    def run(self, item):
        print("printer loaded")
        return item
