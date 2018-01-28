from abc import ABC, abstractmethod
from Implementation.BinInterval import BinInterval
from typing import Dict, List, Set

from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class Discretization(ABC):
    bin_id = 0

    def __init__(self):
        self.property_to_ranges: Dict[int, List[BinInterval]] = {}
        self.bin_count = 0
        self.bin_symbol = -1

    def transform(self, property_id: int, val: TimeStamp):
        while not self.property_to_ranges[property_id][self.bin_id].discretize(val):
            self.bin_id += 1

    @abstractmethod
    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]], property_to_timestamps: Dict[int, List[TimeStamp]]):
        pass

    def set_bin_ranges_from_cutpoints(self, bins_cutpoints):
        for property_id in self.bins_cutpoints.keys():
            bin_cutpoints = self.bins_cutpoints[property_id]
            if len(bin_cutpoints) == 0:
                continue
            bin_ranges = [BinInterval(self.get_symbol(), float('-inf'), bin_cutpoints[0])]
            for i in range(1, len(bin_cutpoints)):
                bin_ranges.append(BinInterval(self.get_symbol(), bin_cutpoints[i-1], bin_cutpoints[i]))
            bin_ranges.append(BinInterval(self.get_symbol(), bin_cutpoints[-1], float('inf')))
            self.property_to_ranges[property_id] = bin_ranges

    def get_symbol(self):
        self.bin_symbol += 1
        return self.bin_symbol

    def discretize(self):
        property_to_entities, class_to_entities, property_to_timestamps = Entity.get_copy_of_maps()
        self.set_bin_ranges(property_to_entities, class_to_entities, property_to_timestamps)
        for property_id in property_to_timestamps.keys():
            if property_id not in self.property_to_ranges:
                continue
            l = sorted(property_to_timestamps[property_id], key=lambda ts: ts.value)
            for val in l:
                self.transform(property_id, val)
            self.bin_id = 0
        return property_to_entities, class_to_entities, property_to_timestamps






