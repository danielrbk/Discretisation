from Implementation.TimeInterval import TimeInterval


class TimeStamp(object):
    def __init__(self, temporal_property_value, time: TimeInterval):
        self.time = time
        self.value = temporal_property_value

    def __str__(self):
        return "<%s , %s>" % (self.value,self.time.__str__())