from Implementation.TimeInterval import TimeInterval


class TimeStamp(object):
    def __init__(self, temporal_property_value, time: TimeInterval):
        self.time = time
        self.value = temporal_property_value
        self.ts_class = None

    def __str__(self):
        return "<%st , %s, %sc>" % (self.time.__str__(), self.value, self.ts_class)

    def __lt__(self, other):
        return self.time < other.time