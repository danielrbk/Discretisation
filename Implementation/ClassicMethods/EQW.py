from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class EqualWidth(Discretization):

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]):
        cutpoints = {}
        for property_id in property_to_timestamps.keys():
            property_values = [ts.value for ts in property_to_timestamps[property_id]]
            min_val = min(property_values)
            max_val = max(property_values)
            interval = (min_val+max_val)/self.bin_count
            cutpoints[property_id] = []
            for i in range(1, self.bin_count):
                cutpoints[property_id].append(min_val + interval*i)
        self.set_bin_ranges_from_cutpoints(cutpoints)

    def __init__(self, bin_count):
        super(EqualWidth, self).__init__()
        self.bin_count = bin_count





