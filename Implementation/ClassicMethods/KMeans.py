from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp

from sklearn.cluster import KMeans as KM
import numpy as np


class KMeans(Discretization):

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]):
        cutpoints = {}
        for property_id in property_to_timestamps.keys():
            property_values = np.array([ts.value for ts in property_to_timestamps[property_id]]).reshape(-1,1)
            kmeans = KM(n_clusters=self.bin_count-1).fit(property_values)
            cutpoints[property_id] = sorted([centroid[0] for centroid in kmeans.cluster_centers_])
        self.bins_cutpoints = cutpoints

    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        pass

    def __init__(self, bin_count):
        super(KMeans, self).__init__()
        self.bin_count = bin_count





