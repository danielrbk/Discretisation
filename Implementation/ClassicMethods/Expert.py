import csv

from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class Expert(Discretization):

    def get_map_used(self):
        return "property_to_timestamps"

    def __init__(self, bins_cutpoints, max_gap, window_size=1):
        super(Expert, self).__init__(max_gap, window_size)
        if isinstance(bins_cutpoints,str):
            self.md5 = bins_cutpoints.split("\\")[-1]
            bins_cutpoints = Expert.load_path_into_dictionary(bins_cutpoints + "\\states.csv")
        self.bins_cutpoints: Dict[int,List[int]] = bins_cutpoints


    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]):
        return self.bins_cutpoints

    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        if not property_to_timestamps and not property_to_entities and not class_to_entities:
            self.load_property_to_timestamps(property_to_timestamps,property_id)
        if property_id not in self.bins_cutpoints:
            return []
        return self.bins_cutpoints[property_id]

    def write_auxiliary_information(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]],
                                    path: str):
        pass

    def get_discretization_name(self):
        return "Expert_%s_%s" % (self.max_gap, self.md5)

    @staticmethod
    def load_path_into_dictionary(path):
        property_to_cutpoints = {}
        states_csv = False
        last_pid = float('-inf')
        with open(path) as f:
            input = csv.reader(f)
            for line in input:
                if line == ["StateID","IntervalClusterID","TemporalPropertyID","TemporalPropertyName",
                            "MethodName","Error1","Entropy","BinID","BinLabel","BinFrom","BinTo",
                            "IntervalClusterLabel","IntervalClusterCentroid","IntervalClusterVariance",
                            "IntervalClusterSize"]:
                    states_csv = True
                elif states_csv:
                    pid = int(line[2])
                    if pid != last_pid:
                        last_pid = pid
                        property_to_cutpoints[pid] = []
                    else:
                        property_to_cutpoints[pid].append(float(line[9]))
                else:
                    property_id = int(line[0])
                    cutpoints = [float(x) for x in line[1:]]
                    property_to_cutpoints[property_id] = cutpoints
        return property_to_cutpoints





