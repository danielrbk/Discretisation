from Implementation.TimeInterval import TimeInterval


class TimeStamp(object):
    def __init__(self, temporal_property_value, time: TimeInterval, ts_class=None):
        self.time = time
        self.value = temporal_property_value
        self.ts_class = ts_class

    def __str__(self):
        if self.ts_class is not None:
            return "<%st , %s, %sc>" % (self.time.__str__(), self.value, self.ts_class)
        else:
            return "<%st , %s>" % (self.time.__str__(), self.value)

    def __lt__(self, other):
        return self.time < other.time