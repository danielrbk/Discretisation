from abc import ABC, abstractmethod
from Implementation.DataObject import DataObject

class Discretisation(ABC):
    alphabet = [chr(ord('A') + i) for i in range(26)] + [chr(ord('a') + i) for i in range(26)]

    def __init__(self, data, bin_count):
        self.data = data
        self.bin_count = bin_count
        self.bin_ranges = [0]*(bin_count-1)
        self.discretised_data = {}

    def transform(self, val):
        for i in range(1, self.bin_count-1):
            if val < self.bin_ranges[i]:
                return self.alphabet[i-1]
        return self.alphabet[self.bin_count - 1]

    @abstractmethod
    def set_bin_ranges(self, values):
        pass

    def discretize(self):
        data = []
        for var in self.data.get_variables():
            values = self.data.get_values_of_variable(var)
            self.set_bin_ranges(values)
            data += [(var, data_point[0], self.transform(data_point[1])) for data_point in values]
        self.discretised_data = DataObject(data)






