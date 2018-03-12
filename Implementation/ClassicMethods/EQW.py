from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class EqualWidth(Discretization):

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]):
        cutpoints = self.parallel_cutpoint_set(property_to_entities, class_to_entities, property_to_timestamps)
        self.bins_cutpoints = cutpoints
        return cutpoints

    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        property_values = [ts.value for ts in property_to_timestamps[property_id]]
        min_val = min(property_values)
        max_val = max(property_values)
        interval = (min_val + max_val) / self.bin_count
        cutpoints = []
        cutpoints = [min_val + interval * i for i in range(1, self.bin_count)]
        return cutpoints


    def __init__(self, bin_count):
        super(EqualWidth, self).__init__()
        self.bin_count = bin_count





