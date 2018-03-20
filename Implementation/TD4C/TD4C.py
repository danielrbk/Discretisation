from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set
from collections import Counter
from Implementation.BinInterval import BinInterval
from Implementation.Constants import EPSILON
from Implementation.Entity import Entity
from Implementation.TimeStamp import TimeStamp
from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.Expert import Expert
from sortedcontainers import SortedList
from math import log
import numpy as np


class TD4C(Discretization):

    def __init__(self, bin_count, distance_measure, ACCURACY_MEASURE = 100):
        super(TD4C, self).__init__()
        self.ACCURACY_MEASURE = ACCURACY_MEASURE
        self.distance_measure = distance_measure
        self.chosen_scores = {}
        self.bin_count = bin_count
        self.candidate_cutpoints = {}
        self.cutoffs_according_to_order = {}

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]], property_to_timestamps: Dict[int, List[TimeStamp]]):
        equal_frequency = EqualFrequency(self.ACCURACY_MEASURE)
        m1,m2,m3 = equal_frequency.discretize(property_to_entities, class_to_entities, property_to_timestamps)
        self.candidate_cutpoints = equal_frequency.bins_cutpoints
        cutpoints = {}
        for p in property_to_timestamps.keys():
            cutpoints[p] = self.set_bin_ranges_for_property(m1, m2, m3, p)
        # cutpoints = self.parallel_cutpoint_set(m1, m2, m3)
        return cutpoints

    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        candidate_cutoffs: List[float] = sorted(self.candidate_cutpoints[property_id])
        chosen_cutoffs = SortedList()
        chosen_cutoffs_indices = SortedList()
        cutoffs_according_to_order = []

        class_to_state_vector = TD4C.populate_state_vector(property_to_entities, class_to_entities, property_to_timestamps, len(candidate_cutoffs), property_id)



        chosen_scores = []
        iterations_scores_and_cutoffs = []
        print("\n---------------------%s----------------------" % property_id)
        for i in range(self.bin_count - 1):
            scores_and_cutoffs = []
            max_distance = float('-inf')
            best_cutoff = float('-inf')
            best_index = float('-inf')
            for j in range(len(candidate_cutoffs)):
                cutoff = candidate_cutoffs[j]
                if j in chosen_cutoffs_indices:
                    continue
                temp_cutoff_indices = chosen_cutoffs_indices.copy()
                temp_cutoff_indices.add(j)
                probability_vector = self.calculate_probability_vector(class_to_state_vector, temp_cutoff_indices)
                distance_of_series = self.distance_measure(probability_vector)
                scores_and_cutoffs.append((cutoff, distance_of_series))
                if distance_of_series > max_distance:
                    max_distance = distance_of_series
                    best_cutoff = cutoff
                    best_index = j
            print("%s: %s" % (best_cutoff, scores_and_cutoffs))
            iterations_scores_and_cutoffs.append(scores_and_cutoffs)
            chosen_cutoffs.add(best_cutoff)
            chosen_cutoffs_indices.add(best_index)
            cutoffs_according_to_order.append(best_cutoff)
            chosen_scores.append(max_distance)

        self.cutoffs_according_to_order.update({property_id: cutoffs_according_to_order})
        self.chosen_scores.update({property_id: chosen_scores})
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
            class_to_probability_vector[c] = [in_state/total if total>0 else 0 for in_state in probability_vector]
        return class_to_probability_vector

    @staticmethod
    def __entropy_measurement__(probability_vector, b):
        return -sum(list(map(lambda x: x*log(x, b) if x > 0 else 0, probability_vector)))

    @staticmethod
    def Entropy(class_to_probability_vector) -> float:
        classes = [TD4C.__entropy_measurement__(class_to_probability_vector[c],len(class_to_probability_vector.keys())) for c in list(class_to_probability_vector.keys())]
        d = 0
        for i in range(len(classes)):
            for j in range(i+1, len(classes)):
                d += abs(classes[i] - classes[j])
        return d

    @staticmethod
    def __cosine__(p1,p2):
        from math import acos
        x = np.array(p1)
        y = np.array(p2)
        sum_p1 = np.sqrt(sum(x**2))
        sum_p2 = np.sqrt(sum(y**2))
        dot = np.dot(x, np.transpose(y))
        if sum_p1 == 0 or sum_p2 == 0:
            return 0
        return acos(dot / (sum_p1*sum_p2))

    @staticmethod
    def Cosine(class_to_probability_vector) -> float:
        classes = list(class_to_probability_vector.keys())
        d = 0
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                d += TD4C.__cosine__(class_to_probability_vector[classes[i]], class_to_probability_vector[classes[j]])
        return d

    @staticmethod
    def __kullback_liebler__(p, q):
        def KL(t):
            pi = t[0]
            qi = t[1]
            if pi == 0:
                return 0
            if qi == 0:
                return pi * log(EPSILON)
            return pi * log(pi/qi)
        try:
            return sum(list(map(KL, zip(p, q))))
        except:
            print(p,q)
            raise

    @staticmethod
    def __SKL__(p,q):
        return (TD4C.__kullback_liebler__(p, q)+TD4C.__kullback_liebler__(q, p)) / 2


    @staticmethod
    def KullbackLiebler(class_to_probability_vector) -> float:
        classes = list(class_to_probability_vector.keys())
        d = 0
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                d += TD4C.__SKL__(class_to_probability_vector[classes[i]],class_to_probability_vector[classes[j]])
        return d

    @staticmethod
    def populate_state_vector(property_to_entities, class_to_entities, property_to_time_stamps, number_of_cutoffs: int, property_id):
        class_to_state_vector = {}
        for c in class_to_entities.keys():
            class_to_state_vector[c] = [0]*(number_of_cutoffs+1)
            ctrs = [Counter([int(ts.value) for ts in entity.properties[property_id]]) for entity in
                    class_to_entities[c] if entity in property_to_entities[property_id]]
            ctr = sum(ctrs, Counter())
            for state in ctr.keys():
                class_to_state_vector[c][state] += ctr[state]
        return class_to_state_vector










