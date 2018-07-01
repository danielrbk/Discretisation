from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Constants import EPSILON, EXTREME_VAL
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class EqualFrequency(Discretization):

    def get_map_used():
        return "property_to_timestamps"

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]):
        cutpoints = self.parallel_cutpoint_set(property_to_entities, class_to_entities, property_to_timestamps)
        return cutpoints

    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        if not property_to_timestamps:
            self.load_property_to_timestamps(property_to_timestamps, property_id)
        property_values = sorted([ts.value for ts in property_to_timestamps[property_id]])
        percentiles = [i/self.bin_count for i in range(1,self.bin_count)]
        max_index = len(property_values) - 1
        indices = [p*max_index for p in percentiles]
        cutpoints = [EqualFrequency.get_cutpoint(i, property_values) for i in indices]
        return list(sorted((set(cutpoints))))
        #return cutpoints

    def write_auxiliary_information(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]],
                                    path: str):
        pass

    def get_discretization_name(self):
        return "EQF_%s" % self.bin_count

    def __init__(self, bin_count, max_gap, window_size=1):
        super(EqualFrequency, self).__init__(max_gap, window_size)
        self.bin_count = int(bin_count)

    @staticmethod
    def load_candidate_cuts(property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]], property_id, bin_count, property_folder):
        eqf = EqualFrequency(bin_count,-1)
        eqf.property_folder = property_folder
        d1,d2,d3 = eqf.discretize_property(property_to_entities,class_to_entities,property_to_timestamps,property_id)
        return d3,eqf.bins_cutpoints

    @staticmethod
    def get_cutpoint(index, property_values):
        from math import floor
        floored_index = floor(index)  # normalize index for arrays
        if floored_index == index:
            index += EPSILON
        if index < 0:
            return -EXTREME_VAL + (index - floored_index) * (property_values[floored_index + 1] + EXTREME_VAL)
        return property_values[floored_index] + (index - floored_index) * (
        property_values[floored_index + 1] - property_values[floored_index])



