from abc import ABC, abstractmethod


class Discretisation(ABC):

    def __init__(self, data, bin_count):
        self.__data = data
        self.bin_count = bin_count
        print(self.bin_count)
        self.__bin_ranges = [0]*(bin_count-1)

    @abstractmethod
    def set_bin_ranges(self):
        pass

    @abstractmethod
    def discretize(self):
        pass






