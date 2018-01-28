from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class EqualFrequency(Discretization):

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]):
        cutpoints = {}
        for property_id in property_to_timestamps.keys():
            property_values = sorted([ts.value for ts in property_to_timestamps[property_id]])
            property_count = len(property_values)
            items_in_bin = property_count / self.bin_count
            cutpoints[property_id] = []
            for i in range(1, self.bin_count):
                cutpoints[property_id].append((property_values[i*items_in_bin-1] + property_values[i*items_in_bin])/2)
        self.bins_cutpoints = cutpoints

    def __init__(self, bin_count):
        super(EqualFrequency, self).__init__()
        self.bin_count = bin_count





