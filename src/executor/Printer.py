from executor.iExecutor import iExecutor


class Printer(iExecutor):
    def run(self, item):
        print(f"printer loaded, item {item}")
        return item
