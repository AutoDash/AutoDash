
ORD_EXCEPTIONS = {
    "esc": 27,
    "enter": 13,
    "backspace": 8,
    "tab": 9
}

def get_ord(key):
    if key in ORD_EXCEPTIONS:
        return ORD_EXCEPTIONS[key]
    if len(key) == 1:
        return ord(key)
    raise NotImplementedError("Not supported keyboard key")


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
