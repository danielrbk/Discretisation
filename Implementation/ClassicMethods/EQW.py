from Implementation.AbstractDiscretisation import Discretization


class EqualWidth(Discretization):

    def __init__(self, data, bin_count):
        super(EqualWidth, self).__init__(data, bin_count)
        self.discretize()

    def set_bin_ranges(self, data_points):
        time_intervals = []
        values = []
        for data_point in data_points:
            values.append(data_point[1])
            time_intervals.append(data_point[0])
        max_val = max(values)
        min_val = min(values)
        block = (max_val-min_val)/self.bin_count
        self.bin_ranges = [min_val+x*block for x in range(1, self.bin_count)]



