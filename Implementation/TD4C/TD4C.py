from Implementation.AbstractDiscretisation import Discretisation
from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.SimpleDiscretization import SimpleDiscretization
from abc import ABC, abstractmethod
from Implementation.DataObject import DataObject


class TD4C(Discretisation):

    def __init__(self, data, bin_count, distance_measure):
        super(TD4C, self).__init__(data, bin_count)
        self.distance_measure = distance_measure
        self.discretize()

    def set_bin_ranges(self, data_points):
        candidate_cutoffs = set(EqualFrequency(self.data, 100).bin_ranges)
        chosen_cutoffs = []
        for i in range(self.bin_count-1):
            max_distance = 0
            best_cutoff = 0
            for cutoff in candidate_cutoffs.difference(chosen_cutoffs):
                j = 0
                temp_cutoffs = chosen_cutoffs.copy()
                while len(chosen_cutoffs) < j and cutoff > chosen_cutoffs[j]:
                    j += 1
                temp_cutoffs.insert(j, cutoff)
                abstracted_series = SimpleDiscretization(self.data,len(temp_cutoffs)+1,temp_cutoffs).discretised_data
                distance_of_series = self.distance_measure(abstracted_series)
                if distance_of_series > max_distance:
                    max_distance = distance_of_series
                    best_cutoff = cutoff
            j = 0
            while len(chosen_cutoffs) < j and best_cutoff > chosen_cutoffs[j]:
                j += 1
            chosen_cutoffs.insert(best_cutoff)











