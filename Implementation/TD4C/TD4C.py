from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set
from collections import Counter
from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp
from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.Expert import Expert
from math import log

class TD4C(Discretization):

    def __init__(self, data, bin_count, distance_measure):
        super(TD4C, self).__init__()
        self.distance_measure = distance_measure
        self.chosen_scores = {}

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]], property_to_timestamps: Dict[int, List[TimeStamp]]):
        chosen_cutoffs = {}
        chosen_scores = {}
        for property_id in property_to_entities.keys():
            p_p2e, p_c2e, p_p2t = self.confine_view_to_property(property_id, property_to_entities, class_to_entities, property_to_timestamps)
            equal_frequency = EqualFrequency(100)
            equal_frequency.discretize(p_p2e, p_c2e, p_p2t)
            candidate_cutoffs: Set[float] = set(equal_frequency.bins_cutpoints[property_id])
            chosen_cutoffs[property_id] = []
            chosen_scores[property_id] = []
            for i in range(self.bin_count-1):
                max_distance = 0
                best_cutoff = 0
                for cutoff in candidate_cutoffs.difference(chosen_cutoffs[property_id]):
                    j = 0
                    temp_cutoffs = chosen_cutoffs[property_id].copy()
                    while len(chosen_cutoffs[property_id]) < j and cutoff > chosen_cutoffs[j]:
                        j += 1
                    temp_cutoffs.insert(j, cutoff)
                    KBD = Expert({property_id: temp_cutoffs})
                    d_p2e, d_c2e, d_p2t = KBD.discretize(p_p2e, p_c2e, p_p2t)
                    distance_of_series = self.distance_measure(len(temp_cutoffs), d_p2e, d_c2e, d_p2t)
                    if distance_of_series > max_distance:
                        max_distance = distance_of_series
                        best_cutoff = cutoff
                j = 0
                while len(chosen_cutoffs[property_id]) < j and best_cutoff > chosen_cutoffs[j]:
                    j += 1
                chosen_cutoffs[property_id].insert(j, best_cutoff)
                chosen_scores[property_id].insert(j, max_distance)
        self.chosen_scores = chosen_scores
        self.bins_cutpoints = chosen_cutoffs

    @staticmethod
    def calculate_probability_vector(cutoff_count: int, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]], property_to_timestamps: Dict[int, List[TimeStamp]]):
        class_to_vector = {}
        key_property = 0
        for key in property_to_entities.keys():
            key_property = key
            break
        for c in class_to_entities:
            class_to_vector[c] = [0]*(cutoff_count+1)
            for entity in class_to_entities[c]:
                ctr = Counter([int(ts.value) for ts in entity.properties[key_property]])
                for state in ctr.keys():
                    class_to_vector[c][state] += ctr[state]
            sum_of_occurrences = sum(class_to_vector[c])
            class_to_vector[c] = [occurrence / sum_of_occurrences for occurrence in class_to_vector[c]]
        return class_to_vector

    @staticmethod
    def __entropy_measurement__(probability_vector):
        return -sum(list(map(lambda x: x*log(x), probability_vector)))

    @staticmethod
    def Entropy(cutoff_count: int, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]], property_to_timestamps: Dict[int, List[TimeStamp]]) -> float:
        class_to_vector = TD4C.calculate_probability_vector(cutoff_count, property_to_entities, class_to_entities, property_to_timestamps)
        classes = [TD4C.__entropy_measurement__(class_to_vector[c]) for c in list(class_to_vector.keys())]
        d = 0
        for i in range(len(classes)):
            for j in range(i+1, len(classes)):
                d += abs(classes[i] - classes[j])
        return d

    @staticmethod
    def __cosine__(p1,p2):
        sum_p1 = sum(list(map(lambda x: x**2, p1)))**0.5
        sum_p2 = sum(list(map(lambda x: x**2, p2)))**0.5
        dot = 0
        for i in range(len(p1)):
            dot += p1[i] * p2[i]
        return dot / (sum_p1*sum_p2)

    @staticmethod
    def Cosine(cutoff_count: int, property_to_entities: Dict[int, Set[Entity]],
                class_to_entities: Dict[int, Set[Entity]], property_to_timestamps: Dict[int, List[TimeStamp]]) -> float:
        class_to_vector = TD4C.calculate_probability_vector(cutoff_count, property_to_entities, class_to_entities,
                                                            property_to_timestamps)
        classes = list(class_to_vector.keys())
        d = 0
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                d += TD4C.__cosine__(class_to_vector[classes[i]], class_to_vector[classes[j]])
        return d









