from sortedcontainers import SortedList

from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set, Counter

from Implementation.BinInterval import BinInterval
from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.Constants import EPSILON
from Implementation.Entity import Entity
from Implementation.TD4C.TD4C import TD4C
from Implementation.TimeStamp import TimeStamp

from sklearn.cluster import KMeans as KM
import numpy as np


class Persist(Discretization):
    def __init__(self, bin_count):
        super(Persist, self).__init__()
        self.bin_count = int(bin_count)

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]) -> Dict[int, List[float]]:
        equal_frequency = EqualFrequency(100)
        m1, m2, m3 = equal_frequency.discretize(property_to_entities, class_to_entities, property_to_timestamps)
        self.candidate_cutpoints = equal_frequency.bins_cutpoints
        cutpoints = {}
        for p in property_to_timestamps.keys():
            cutpoints[p] = self.set_bin_ranges_for_property(m1,m2,m3,p)
        #cutpoints = self.parallel_cutpoint_set(m1, m2, m3)
        return cutpoints

    def get_discretization_name(self) -> str:
        pass

    def write_auxiliary_information(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]], path: str) -> None:
        pass

    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int) -> List[
        float]:
        candidate_cutoffs: List[float] = sorted(self.candidate_cutpoints[property_id])
        print("%s: %s" % (property_id,candidate_cutoffs))
        state_count = (len(candidate_cutoffs) + 1)
        A = np.zeros(shape=(state_count, state_count))
        state_vector = [0]*state_count
        chosen_cutoffs = SortedList()
        chosen_cutoffs_indices = SortedList()

        for e in property_to_entities[property_id]:
            time_stamps = sorted(e.properties[property_id])

            for i in range(len(time_stamps)-1):
                prev = time_stamps[i]
                now = time_stamps[i+1]
                A[now.value][prev.value] += 1
                state_vector[prev.value] += 1
            state_vector[time_stamps[-1].value] += 1

        for i in range(self.bin_count - 1):
            max_distance = float('-inf')
            best_cutoff = float('-inf')
            best_index = float('-inf')
            for j in range(len(candidate_cutoffs)):
                cutoff = candidate_cutoffs[j]
                if j in chosen_cutoffs_indices:
                    continue
                temp_cutoff_indices = chosen_cutoffs_indices.copy()
                temp_cutoff_indices.add(j)
                new_A = self.collapse_matrix(A, temp_cutoff_indices)
                distance_of_series = self.distance_measure(new_A, state_vector)
                if distance_of_series > max_distance:
                    max_distance = distance_of_series
                    best_cutoff = cutoff
                    best_index = j
            chosen_cutoffs.add(best_cutoff)
            chosen_cutoffs_indices.add(best_index)

        return list(chosen_cutoffs)

    @staticmethod
    def collapse_matrix(A, cut_points):
        new_dimension = len(cut_points) + 1
        new_A = np.zeros(shape=(new_dimension, new_dimension))
        row_matrices = []
        prev = 0
        for i in range(len(cut_points)):
            cut = cut_points[i] + 1
            row_matrices.append(A[prev:cut])
            prev = cut
        row_matrices.append(A[prev:])
        C = []
        try:
            for i in range(new_dimension):
                B = row_matrices[i]
                prev = 0
                for j in range(len(cut_points)):
                    cut = cut_points[j]+1
                    C = B.transpose()[prev:cut]
                    prev = cut
                    new_A[i][j] = sum(sum(C))
                C = B.transpose()[prev:]
                new_A[i][-1] = sum(sum(C))
        except:
            print("C:",C)
            print("A:",A)
            print(cut_points)
            raise

        return new_A

    @staticmethod
    def distance_measure(new_A, state_vector):
        total = sum(state_vector)
        marginal_sum = sum(new_A)
        s = 0
        c = 0
        for i in range(len(new_A)):
            total_probability = state_vector[i] / total
            if total_probability == 0:
                continue
            c+=1
            if state_vector[i] == 0:
                continue
            sign = 1
            if marginal_sum[i] == 0:
                marginal_probability = 0
            else:
                marginal_probability = new_A[i][i] / marginal_sum[i]
            if marginal_probability == 0:
                marginal_probability += EPSILON
            elif marginal_probability == 1:
                marginal_probability -= EPSILON
            if total_probability == 1:
                total_probability -= EPSILON

            if marginal_probability > total_probability:
                sign = 1
            elif marginal_probability == total_probability:
                sign = 0
            else:
                sign = -1

            s += sign*Persist.discrete_kullback_liebler(marginal_probability,total_probability)
        return s / len(new_A)

    @staticmethod
    def discrete_kullback_liebler(p, q):
        return TD4C.__SKL__([p, 1-p], [q, 1-q])






