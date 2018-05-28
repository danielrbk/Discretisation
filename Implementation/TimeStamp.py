import sys
from ctypes import c_int, c_uint, c_float

from Implementation.TimeInterval import TimeInterval
from struct import *


class TimeStamp(object):
    def __init__(self, temporal_property_value, start: int, end, entity_id: int, ts_class=-10000):
        self.start_point = start
        self.end_point = end
        self.value = temporal_property_value
        self.ts_class = int(ts_class)
        self.entity_id = entity_id

    def __str__(self):
        timestr = [self.start_point, self.end_point].__str__() if self.start_point!=self.end_point else self.start_point.__str__()
        if self.ts_class is not None:
            return "<%st , %s, %sc>" % (timestr, self.value, self.ts_class)
        else:
            return "<%st , %s>" % (timestr, self.value)

    def __lt__(self, other):
        return self.start_point < other.start_point or \
               (self.start_point == other.start_point and self.end_point < other.end_point)

    def deep_copy(self) -> 'TimeStamp':
        return TimeStamp(self.value,self.start_point,self.end_point,self.entity_id,self.ts_class)

if __name__ == "__main__":
    row = "20000,5,3,0.6".split(",")
    ts = TimeStamp(float(row[-1]),3,int(row[0]),5)
    mem_size = sys.getsizeof(ts)
    print("Real:%s" %mem_size)
