
class IndexedRect(object):
    def __init__(self, i, x1, y1, x2, y2):
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.i = i

    def __str__(self):
        return "[({0},{1}),({2},{3})]".format(
            self.x1,
            self.y1,
            self.x2,
            self.y2
        )

    def get_points(self):
        return [(self.x1,self.y1),(self.x2,self.y2)]
    def get_flat_points(self):
        return [self.x1,self.y1,self.x2,self.y2]