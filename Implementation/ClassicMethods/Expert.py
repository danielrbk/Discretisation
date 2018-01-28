from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp


class Expert(Discretization):

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]):
        pass

    def __init__(self, bins_cutpoints: Dict[int, List[int]]):
        super(Expert, self).__init__()
        self.bins_cutpoints: Dict[int,List[int]] = bins_cutpoints





