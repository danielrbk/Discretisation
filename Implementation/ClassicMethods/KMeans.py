from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp

from sklearn.cluster import KMeans as KM
import numpy as np


class KMeans(Discretization):
    @staticmethod
    def get_map_used():
        return "property_to_timestamps"

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]):
        cutpoints = {}
        for property_id in property_to_timestamps.keys():
            cutpoints[property_id] = self.set_bin_ranges_for_property(property_to_entities,class_to_entities,property_to_timestamps,property_id)
        return cutpoints

    def write_auxiliary_information(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]],
                                    path: str):
        pass

    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        if not property_to_timestamps:
            self.load_property_to_timestamps(property_to_timestamps, property_id)
        property_values = np.array([ts.value for ts in property_to_timestamps[property_id]]).reshape(-1, 1)
        kmeans = KM(n_clusters=self.bin_count - 1).fit(property_values)
        return list(sorted([centroid[0] for centroid in kmeans.cluster_centers_]))

    def get_discretization_name(self):
        return "KMeans_%s" % self.bin_count


    def __init__(self, bin_count, max_gap, window_size=1):
        super(KMeans, self).__init__(max_gap, window_size)
        self.bin_count = int(bin_count)





