from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set
from collections import Counter
from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp
from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.Expert import Expert
from sortedcontainers import SortedList
from math import log
import numpy as np


class TD4C(Discretization):

    def __init__(self, bin_count, distance_measure):
        super(TD4C, self).__init__()
        self.distance_measure = distance_measure
        self.chosen_scores = {}
        self.bin_count = bin_count
        self.candidate_cutpoints = {}

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]], property_to_timestamps: Dict[int, List[TimeStamp]]):
        equal_frequency = EqualFrequency(100)
        m1,m2,m3 = equal_frequency.discretize(property_to_entities, class_to_entities, property_to_timestamps)
        self.candidate_cutpoints = equal_frequency.bins_cutpoints
        cutpoints = self.parallel_cutpoint_set(m1, m2, m3)
        return cutpoints

    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        candidate_cutoffs: List[float] = sorted(self.candidate_cutpoints[property_id])
        chosen_cutoffs = SortedList()
        chosen_cutoffs_indices = SortedList()
        cutoffs_according_to_order = []

        class_to_state_vector = {}

        for c in class_to_entities.keys():
            class_to_state_vector[c] = [0]*(len(candidate_cutoffs)+1)
            ctrs = [Counter([int(ts.value) for ts in entity.properties[property_id]]) for entity in
                    class_to_entities[c] if entity in property_to_entities[property_id]]
            ctr = sum(ctrs, Counter())
            for state in ctr.keys():
                class_to_state_vector[c][state] += ctr[state]

        chosen_scores = []

        for i in range(self.bin_count - 1):
            max_distance = 0
            best_cutoff = 0
            best_index = 0
            for j in range(len(candidate_cutoffs)):
                cutoff = candidate_cutoffs[j]
                if cutoff in chosen_cutoffs:
                    continue
                temp_cutoff_indices = chosen_cutoffs_indices.copy()
                temp_cutoff_indices.add(j)
                probability_vector = self.calculate_probability_vector(class_to_state_vector, temp_cutoff_indices)
                distance_of_series = self.distance_measure(probability_vector)
                if distance_of_series > max_distance:
                    max_distance = distance_of_series
                    best_cutoff = cutoff
                    best_index = j
            chosen_cutoffs.add(best_cutoff)
            chosen_cutoffs_indices.add(best_index)
            cutoffs_according_to_order.append(best_cutoff)
            chosen_scores.append(max_distance)

        self.chosen_scores.update({property_id:chosen_scores})
        return list(chosen_cutoffs)

    def write_auxiliary_information(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]],
                                    path: str):
        pass

    def get_discretization_name(self):
        return "TD4C_%s_%s" % (self.method_name(),self.bin_count)

    def method_name(self):
        if self.distance_measure == TD4C.Cosine:
            return "Cosine"
        elif self.distance_measure == TD4C.Entropy:
            return "Entropy"
        elif self.distance_measure == TD4C.KullbackLiebler:
            return "KullbackLiebler"

    @staticmethod
    def calculate_probability_vector(class_to_state_vector, curr_cutoffs):
        class_to_probability_vector = {}
        for c in class_to_state_vector.keys():
            state_vector = class_to_state_vector[c]
            startIndex = 0
            state = 0
            total = 0
            probability_vector = [0]*(len(curr_cutoffs)+1)
            for index in curr_cutoffs:
                endIndex = index + 1
                in_state = sum(state_vector[startIndex:endIndex])
                probability_vector[state] = in_state
                total += in_state
                startIndex = endIndex
                state += 1
            in_state = sum(state_vector[startIndex:])
            total += in_state
            probability_vector[state] = in_state
            class_to_probability_vector[c] = [in_state/total for in_state in probability_vector]
        return class_to_probability_vector

    @staticmethod
    def __entropy_measurement__(probability_vector):
        return -sum(list(map(lambda x: x*log(x), probability_vector)))

    @staticmethod
    def Entropy(class_to_probability_vector) -> float:
        classes = [TD4C.__entropy_measurement__(class_to_probability_vector[c]) for c in list(class_to_probability_vector.keys())]
        d = 0
        for i in range(len(classes)):
            for j in range(i+1, len(classes)):
                d += abs(classes[i] - classes[j])
        return d

    @staticmethod
    def __cosine__(p1,p2):
        x = np.array(p1)
        y = np.array(p2)
        sum_p1 = np.sqrt(sum(x**2))
        sum_p2 = np.sqrt(sum(y**2))
        dot = np.dot(x, np.transpose(y))
        return dot / (sum_p1*sum_p2)

    @staticmethod
    def Cosine(class_to_probability_vector) -> float:
        classes = list(class_to_probability_vector.keys())
        d = 0
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                d += TD4C.__cosine__(class_to_probability_vector[classes[i]], class_to_probability_vector[classes[j]])
        return d

    @staticmethod
    def __kullback_liebler__(p,q):
        return sum(list(map(lambda t: t[0] * log(t[0]/t[1]), zip(p, q))))

    @staticmethod
    def __SKL__(p,q):
        return (TD4C.__kullback_liebler__(p,q)+TD4C.__kullback_liebler__(q,p)) / 2


    @staticmethod
    def KullbackLiebler(class_to_probability_vector) -> float:
        classes = class_to_probability_vector.keys()
        d = 0
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                d += TD4C.__SKL__(class_to_probability_vector[i],class_to_probability_vector[j])
        return d









