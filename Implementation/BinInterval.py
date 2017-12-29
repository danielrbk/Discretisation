from Implementation.TimeStamp import TimeStamp


class BinInterval(object):
    def __init__(self, bin_symbol: int, min_val: float, max_val: float):
        self.bin_symbol = bin_symbol
        self.min_val = min_val
        self.max_val = max_val

    def discretize(self, time_stamp: TimeStamp) -> bool:
        if self.min_val <= time_stamp.value < self.max_val:
            time_stamp.value = self.bin_symbol
            return True
        return False

    def __eq__(self, other):
        return self.min_val == other.min_val and self.max_val == other.max_val

    def __lt__(self, other):
        return self.min_val < other.min_val or \
               (self.min_val == other.min_val and self.max_val < other.max_val)




