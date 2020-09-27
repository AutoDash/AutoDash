
class RotatingLog(object):
    def __init__(self, size):
        self.logs = ["" for _ in range(size)]
        self.index = 0
        self.size = size

    def log(self, msg: str):
        self.logs[self.index] = msg
        self.index = (self.index + 1) % self.size

    def get_logs(self):
        ret = self.logs[self.index:] + self.logs[:self.index]
        return ret