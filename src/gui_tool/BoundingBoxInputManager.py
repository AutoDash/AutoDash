
from .IndexedRect import IndexedRect

class IndexedRectBuilder(object):
    def __init__(self):
        self.last_rect = None
        self.initial_point = None
        self.reset()

    def set_initial_point(self, x, y):
        self.initial_point = (x,y)

    def get_initial_point(self):
        return self.initial_point

    def reset(self):
        self.last_rect = None
        self.initial_point = None

    def has_initial_point(self):
        return self.initial_point is not None

    def to_rect(self, i, x, y):
        self.last_rect = IndexedRect(i, self.initial_point[0], self.initial_point[1], x, y)
        self.initial_point = None
        return self.last_rect

class BoundingBoxInputManager(object):
    MAX_KEPT = 20
    def __init__(self):
        self.curr_inputs = []
        self.reset()

    def add(self, ir: IndexedRect):
        self.curr_inputs.append(ir)
        self.curr_inputs = self.curr_inputs[-self.MAX_KEPT:]

    def get_n(self):
        return min(len(self.curr_inputs), 2)

    def has_n(self, n):
        return len(self.curr_inputs) >= n

    def reset(self):
        self.curr_inputs = []

    def __getitem__(self, key):
        return self.curr_inputs[-2:][key]

    def get_2_sorted(self):
        return sorted(self.curr_inputs[-2:], key=lambda r: r.i)

    def get_last(self):
        if len(self.curr_inputs) == 0:
            return None
        return self.curr_inputs[-1]

    def remove_last(self):
        if self.has_n(1):
            last = self.curr_inputs[-1]
        else:
            last = None
        self.curr_inputs = self.curr_inputs[:-1]
        return last