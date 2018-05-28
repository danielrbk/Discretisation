import csv

from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class Expert(Discretization):

    def get_map_used(self):
        return "absolutely none"

    def __init__(self, bins_cutpoints, max_gap):
        super(Expert, self).__init__(max_gap)
        if isinstance(bins_cutpoints,str):
            bins_cutpoints = Expert.load_path_into_dictionary(bins_cutpoints)
        self.bins_cutpoints: Dict[int,List[int]] = bins_cutpoints

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]):
        return self.bins_cutpoints

    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        return self.bins_cutpoints[property_id]

    def write_auxiliary_information(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]],
                                    path: str):
        pass

    def get_discretization_name(self):
        return "Expert"

    @staticmethod
    def load_path_into_dictionary(path):
        property_to_cutpoints = {}
        with open(path) as f:
            input = csv.reader(f)
            for line in input:
                property_id = line[0]
                cutpoints = line[1:]
                property_to_cutpoints[property_id] = cutpoints
        return property_to_cutpoints





