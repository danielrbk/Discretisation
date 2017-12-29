from abc import ABC, abstractmethod
from Implementation.BinInterval import BinInterval
from typing import Dict, List, Set

from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class Discretization(ABC):
    bin_id = 0

    def __init__(self):
        self.property_to_ranges: Dict[int, List[BinInterval]] = {}
        self.bin_number = 0

    def transform(self, property_id: int, val: TimeStamp):
        while not self.property_to_ranges[property_id][self.bin_number].discretize(val):
            self.bin_id += 1

    @abstractmethod
    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]], property_to_timestamps: Dict[int, List[TimeStamp]]):
        pass

    def discretize(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]], property_to_timestamps: Dict[int, List[TimeStamp]]):
        self.set_bin_ranges(property_to_entities, class_to_entities, property_to_timestamps)
        for property_id in property_to_timestamps.keys():
            l = sorted(property_to_timestamps[property_id], key=lambda ts: ts.value)
            for val in l:
                self.transform(property_id, val)









