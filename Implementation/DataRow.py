from ctypes import c_int, c_uint, c_float

from Implementation.Constants import FileFormatNotCorrect
from Implementation.TimeStamp import TimeStamp
from Implementation.TimeInterval import TimeInterval


class DataRow(object):
    def __init__(self, entity_id: int, temporal_property_id: int, time_stamp: TimeStamp):
        self.entity_id: int = entity_id
        self.temporal_property_id: int = temporal_property_id
        self.time_stamp = time_stamp

    def get_entity_id(self) -> int:
        return self.entity_id

    def get_temporal_property_id(self) -> int:
        return self.temporal_property_id

    def get_time_stamp(self) -> TimeStamp:
        return self.time_stamp

    @staticmethod
    def get_data_from_row(line: str) -> 'DataRow':
        try:
            line = line.rstrip().split(',')
            eid = int(line[0])
            tid = int(line[1])
            time = int(line[2])
            val = float(line[3])
        except:
            raise FileFormatNotCorrect()
        time_stamp = TimeStamp(val, time,time, eid)
        return DataRow(eid, tid, time_stamp)

