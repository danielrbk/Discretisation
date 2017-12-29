from Implementation.AbstractDiscretisation import Discretization


class EqualFrequency(Discretization):

    def __init__(self, data, bin_count):
        super(EqualFrequency, self).__init__(data, bin_count)
        self.discretize()

    def set_bin_ranges(self, data_points):
        time_intervals = []
        values = []
        for data_point in data_points:
            values.append(data_point[1])
            time_intervals.append(data_point[0])
        mod = len(values) % self.bin_count
        stacking_remainder = 0
        num_in_bin = len(values) // self.bin_count + 1
        ctr = 0
        for i in range(num_in_bin-1, len(values), num_in_bin):
            if mod > 0:
                mod = (mod + 1) % self.bin_count
                stacking_remainder += 1
            i -= stacking_remainder
            self.bin_ranges[ctr] = (values[i] + values[i+1])/2
            ctr += 1




