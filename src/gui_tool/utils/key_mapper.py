
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


class KeyMapper(object):
    def __init__(self):
        self.reverse_ord = {}
        self.curr = []

    def append(self, inp: int):
        if inp == 255:
            return  # No input
        self.curr.append(inp)

    def reset(self):
        self.curr = []

    def consume(self, keys):
        if isinstance(keys, str):
            keys = (get_ord(keys),)
        else:
            keys = tuple([get_ord(key) for key in keys])
        l = len(keys)

        if tuple(self.curr[-l:]) == keys:
            self.reset()
            return True
        else:
            return False
