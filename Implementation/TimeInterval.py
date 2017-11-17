class TimeInterval:
    def __init__(self, start_point, end_point):
        self.start_point = start_point
        self.end_point = end_point

    def __eq__(self, other):
        return self.start_point == other.start_point and self.end_point == other.end_point

    def __lt__(self, other):
        return self.start_point < other.start_point or \
               (self.start_point == other.start_point and self.end_point < other.end_point)

    def __str__(self):
        return [self.start_point, self.end_point].__str__()

