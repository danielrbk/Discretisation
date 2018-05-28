from ctypes import c_uint


class TimeInterval:
    def __init__(self, start_point, end_point):
        self.start_point = c_uint(start_point)
        self.end_point = c_uint(end_point)

    def __lt__(self, other):
        return self.start_point < other.start_point or \
               (self.start_point == other.start_point and self.end_point < other.end_point)

    def __str__(self):
        return [self.start_point, self.end_point].__str__() if self.start_point!=self.end_point else self.start_point.__str__()

