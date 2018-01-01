from Implementation.AbstractDiscretisation import Discretisation


class SimpleDiscretization(Discretisation):

    def __init__(self, data, bin_count, bin_ranges):
        super(SimpleDiscretization, self).__init__(data, bin_count)
        self.bin_ranges = bin_ranges
        self.discretize()

    def set_bin_ranges(self, data_points):
        pass



