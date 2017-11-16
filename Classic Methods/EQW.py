from AbstractDiscretisation import Discretisation


class EqualWidth(Discretisation):

    def __init__(self, data, bin_count):
        super(EqualWidth, self).__init__(data, bin_count)
        self.bin_count = self.bin_count + 1
        print(self.bin_count)

    def set_bin_ranges(self):


    def discretize(self):
        pass


EqualWidth([1,2,3],4)