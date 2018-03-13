from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


def entropy (class_list, proportion):
    for i, val in enumerate(class_list):
        pass

# class EqualFrequency(Discretization):
#
#     def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
#                        property_to_timestamps: Dict[int, List[TimeStamp]]):
#         cutpoints = self.parallel_cutpoint_set(property_to_entities, class_to_entities, property_to_timestamps)
#         return cutpoints
#
#     def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
#                        property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
#         # sorting property values
#         property_values = sorted([ts.value for ts in property_to_timestamps[property_id]])
#         property_count = len(property_values)
#
#
#
#         items_in_bin = property_count // self.bin_count
#         cutpoints = list(set([((property_values[i * items_in_bin - 1] + property_values[i * items_in_bin]) / 2) for
#                                   i in range(1, self.bin_count)]))
#         return cutpoints
#
#     def write_auxiliary_information(self, property_to_entities: Dict[int, Set[Entity]],
#                                     class_to_entities: Dict[int, Set[Entity]],
#                                     property_to_timestamps: Dict[int, List[TimeStamp]],
#                                     path: str):
#         pass
#
#     def get_discretization_name(self):
#         return "EQF_%s" % self.bin_count


    def __init__(self, bin_count):
        super(EqualFrequency, self).__init__()
        self.bin_count = bin_count





