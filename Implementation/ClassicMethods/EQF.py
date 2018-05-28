from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class EqualFrequency(Discretization):

    def get_map_used(self):
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
        property_count = len(property_values)

        def get_index(percent, property_count):
            '''
            Get indices of the property values which induce the cuts used in the discretisation
            :param percent:
            :param property_count:
            :return:
            '''
            x = percent * property_count + 0.5  # 0.5 will be explained later
            if x >= property_count:
                x = property_count - 1
            elif x < 1:
                x = 1
            return x

        def get_cutpoint(index, property_values):
            '''

            :param index:
            :param property_values:
            :return:
            '''
            from math import floor
            floored_index = floor(index)  # normalize index for arrays
            return property_values[floored_index - 1] + (index - floored_index) * (property_values[floored_index] - property_values[floored_index-1])

        indices = [get_index(percent, property_count) for percent in percentiles]
        cutpoints = [get_cutpoint(i, property_values) for i in indices]
        return list(sorted((set(cutpoints))))
        #return cutpoints

    def write_auxiliary_information(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]],
                                    path: str):
        pass

    def get_discretization_name(self):
        return "EQF_%s" % self.bin_count

    def __init__(self, bin_count, max_gap):
        super(EqualFrequency, self).__init__(max_gap)
        self.bin_count = int(bin_count)

    @staticmethod
    def load_candidate_cuts(property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]], property_id, bin_count, property_folder):
        eqf = EqualFrequency(bin_count,-1)
        eqf.property_folder = property_folder
        d1,d2,d3 = eqf.discretize_property(property_to_entities,class_to_entities,property_to_timestamps,property_id)
        return d3,eqf.bins_cutpoints






