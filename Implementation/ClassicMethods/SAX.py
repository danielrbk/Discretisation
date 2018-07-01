from sortedcontainers import SortedList
from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set, Counter, Tuple

from Implementation.BinInterval import BinInterval
from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.Constants import EPSILON
from Implementation.Entity import Entity
from Implementation.TD4C.TD4C import TD4C
from Implementation.TimeStamp import TimeStamp
from Implementation.AbstractDiscretisation import Discretization
from sklearn.cluster import KMeans as KM
import numpy as np

from pandas import DataFrame
from scipy.stats import norm
import numpy as np

from Implementation.AbstractDiscretisation import Discretization


class SaxConstrainsException(Exception): pass


class SAX(Discretization):
    def get_map_used():
        return "property_to_timestamps"

    def __init__(self, bin_count, max_gap, window_size=1):
        super(SAX, self).__init__(max_gap, window_size)
        self.bin_count = int(bin_count)
        self.window_size = int(window_size)
        self.SAX_OBJECT = __SAX__(int(window_size),int(bin_count),alphabet=[str(i) for i in range(int(bin_count))])

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]) -> Dict[int, List[float]]:
        cutpoints = {}
        for p in property_to_timestamps.keys():
            cutpoints[p] = self.set_bin_ranges_for_property(property_to_entities,class_to_entities,property_to_timestamps,p)
        return cutpoints

    def get_discretization_name(self) -> str:
        return "SAX_%s_%s" % (self.bin_count,self.max_gap)

    def write_auxiliary_information(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]], path: str) -> None:
        pass

    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int) -> List[
        float]:
        if not property_to_timestamps:
            self.load_property_to_timestamps(property_to_timestamps, property_id)
        return self.SAX_OBJECT.perform_discretization_framework(property_to_timestamps)

    def discretize_property(self, property_to_entities: Dict[int, Set[Entity]],
                            class_to_entities: Dict[int, Set[Entity]],
                            property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int) -> Tuple[
        Dict[int, Set['Entity']], Dict[int, Set['Entity']], Dict[int, List[TimeStamp]]]:
        new_p2t = self.get_copy_of_property_to_timestamps(property_to_timestamps)
        self.bins_cutpoints[property_id] = self.set_bin_ranges_for_property(property_to_entities, class_to_entities,
                                                                            new_p2t, property_id)
        self.set_bin_ranges_from_cutpoints_for_property(property_id)
        self.abstract_property_in_property_to_timestamps(new_p2t,property_id)
        return property_to_entities,class_to_entities,new_p2t


class __SAX__(object):
    """
    This class is for computing common things with the Symbolic
    Aggregate approXimation method.  In short, this translates
    a series of data to a string.
    """

    def __init__(self, points_amount=4, alphabet_size=7, alphabet=None, epsilon=1e-6):

        if points_amount < 1:
            raise SaxConstrainsException('word size must be at least 1, given ' + str(points_amount))

        if alphabet is None and alphabet_size is None:
            raise SaxConstrainsException('alphabet parameters not given, alphabet_size or alphabet must be set!')

        if alphabet is None and alphabet_size < 2:
            raise SaxConstrainsException('alphabet size should be grater then 1, given ' + str(alphabet_size))

        if alphabet is not None and len(alphabet) < 2:
            raise SaxConstrainsException('alphabet length should be grater then 1, given ' + alphabet)

        if alphabet is None:
            self._alphabet = self.__generate_alphabet(alphabet_size)
        else:
            self._alphabet = alphabet

        self._alphabet_size = len(self._alphabet)

        self._word_size = 0

        self._points_amount = points_amount

        self._epsilon = epsilon

        # TODO is it needed?
        # self._limits = self.__build_limits(self._alphabet_size)

    def __generate_alphabet(self, size):
        alphabet = []
        alphabet.append(ord('a'))
        for index in range(1, size):
            alphabet.append(alphabet[index - 1] + 1)
        return [chr(element) for element in alphabet]

    @staticmethod
    def build_limits(size):
        return [norm.ppf(part / size) for part in range(1, size)]

    def normalize(self, values):
        """
        Function will normalize an array (give it a mean of 0, and a
        standard deviation of 1) unless it's standard deviation is below
        epsilon, in which case it returns an array of zeros the length
        of the original array.
        """
        values = np.asanyarray(values);
        std = values.std()
        mean = values.mean();
        if std < self._epsilon:
            raise SaxConstrainsException('Values Standard Deviation is less then current epsilon');
        return (values - mean) / std

    def __to_paa(self, values):
        """
        Performs Piecewise Aggregate Approximation on a given values, reducing
        the dimension of the values length n to w approximations.
        each value from the approximations is the mean of frame size values.
        returns the reduced dimension data set, as well as the indices corresponding to the original
        data for each reduced dimension.
        """
        values_length = len(values)

        frame_size = int(np.math.ceil(values_length / float(self._word_size)))

        frame_start = 0

        approximation = []

        indices_ranges = []

        loop_limit = values_length - frame_size

        while frame_start <= loop_limit:
            to = int(frame_start + frame_size)
            indices_ranges.append((frame_start, to))
            approximation.append(np.mean(np.array(values[frame_start: to])))
            frame_start += frame_size

        # handle the remainder if n % w != 0
        if frame_start < values_length:
            indices_ranges.append((frame_start, values_length))
            approximation.append(np.mean(np.array(values[frame_start: values_length])))

        return np.array(approximation), indices_ranges

    def to_paa(self, values):
        """
        Performs Piecewise Aggregate Approximation on a given values, reducing
        the dimension of the values length n to w approximations.
        each value from the approximations is the mean of frame size values.
        returns the reduced dimension data set, as well as the indices corresponding to the original
        data for each reduced dimension.
        """
        values_length = len(values)

        frame_size = self._points_amount

        frame_start = 0

        approximation = []

        indices_ranges = []

        loop_limit = values_length - frame_size

        while frame_start <= loop_limit:
            to = int(frame_start + frame_size)
            indices_ranges.append((frame_start, to))
            approximation.append(np.mean(np.array(values[frame_start: to])))
            frame_start += frame_size

        # handle the remainder if n % w != 0
        if frame_start < values_length:
            indices_ranges.append((frame_start, values_length))
            approximation.append(np.mean(np.array(values[frame_start: values_length])))

        return np.array(approximation), indices_ranges

    def __convert_to_symbols(self, values, column=None):
        """
        Converts the Piecewise Aggregate Approximation of x to a series of letters.
        compute the needed index by computing Cumulative distribution function and dividing by the distribution part size.
        """
        symbols = []
        part_size = 1 / self._alphabet_size
        extra = ''
        if column is not None:
            extra=str(column)
        for value in values:
            index = int(norm.cdf(value) / part_size)
            if index == self._alphabet_size: # handle edge case of norm.cdf(value) == 1.0
                index -= 1
            symbols.append(self._alphabet[index] + extra)
        return symbols

    def to_symbols(self, values, column=None):
        """
        Function takes a series of data, x, and transforms it to a string representation
        """
        if self._points_amount > len(values):
            raise SaxConstrainsException(
                'given values length: ' + str(len(values)) + ', is less then word size: ' + str(self._points_amount))
        length = len(values)

        self._word_size = int(length / self._points_amount)

        if length % self._points_amount != 0:
            self._word_size +=1

        (values_as_paa, indices) = self.__to_paa(self.normalize(values))
        return self.__convert_to_symbols(values_as_paa, column), indices

    def perform_discritization(self, data_frame, with_columns=False):
        ans = {}
        for column in data_frame:
            if with_columns:
                symbols_data = self.to_symbols(data_frame[column].values.tolist(), column)
            else:
                symbols_data = self.to_symbols(data_frame[column].values.tolist())
            ans[column] = symbols_data[0]

        return DataFrame(ans)

    def perform_discretization_framework(self, property_to_timestamps):
        for property_id in property_to_timestamps:
            values = [x.value for x in property_to_timestamps[property_id]]
            symbols_data = self.to_symbols(values)[0]
            for i in range(len(symbols_data)):
                for j in range(self._points_amount):
                    symbol = int(symbols_data[i])
                    index = self._points_amount*i+j
                    if index < len(property_to_timestamps[property_id]):
                        property_to_timestamps[property_id][index].value = symbol
                    else:
                        break
        return self.build_limits(self._alphabet_size)

    def discretize(self, p2e, c2e, p2t):
        m1,m2,m3 = Discretization.get_copy_of_maps(p2e,c2e,p2t)
        cutpoints = self.perform_discretization_framework(m3)
        return m1,m2,m3,cutpoints


def use_sax(bin_count,window_size,p2e,c2e,p2t):
    sax = __SAX__(int(window_size),int(bin_count))
    return sax.discretize(p2e,c2e,p2t)

if __name__ == '__main__':
    max_bin = 3
    sax = __SAX__(points_amount=3, alphabet=[str(i) for i in range(max_bin)])
    df = DataFrame(np.random.randint(0, 556, size=1668))
    print(df)
    df_disc = sax.perform_discritization(df, False)
    print(df_disc)