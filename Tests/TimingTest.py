import csv
import timeit
import unittest
from typing import Dict, List

from Implementation.AbstractDiscretisation import Discretization
from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.ClassicMethods.Expert import Expert
from Implementation.ClassicMethods.Persist import Persist
from Implementation.Entity import Entity
from Implementation.InputHandler import get_maps_from_file
from Implementation.TimeInterval import TimeInterval
from Implementation.TD4C.TD4C import TD4C
from Implementation.TimeStamp import TimeStamp
from Tests.Discretization_Result_Generator import get_test_result, print_maps
from Tests.Constants import DATASETS_PATH

DATASET_NAME = "TestDataSet"
CLASS_SEPERATOR = 55

DATASET_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + ".csv"
EXPECTED_OUTPUT_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + "_"

m1 = None
m2 = None
m3 = None
r1 = None
r2 = None
r3 = None


def read_file():
    global m1, m2, m3
    print("Reading file...")
    m1, m2, m3 = get_maps_from_file(DATASET_PATH, CLASS_SEPERATOR, True)


def copy_maps():
    global r1,r2,r3,m1,m2,m3
    print("Copying...")
    r1, r2, r3 = Discretization.get_copy_of_maps(m1, m2, m3)


def compare_maps():
    global r1,r2,r3,m1,m2,m3
    print("Comparing...")
    print(r1==m1)
    print(r2==m2)
    print(r3==m3)


def discretize():
    global m1,m2,m3
    d = Expert({44: [0.74], 3: [26], 4:[21], 5:[70]}, max_gap=1)
    d1,d2,d3 = d.discretize(m1,m2,m3)
    print_maps(d1,d2,d3)




'''
class TimingTest(unittest.TestCase):
    def test_small_file_read(self):
        d = EqualWidth(3)
        name = "EQW3"
        a = timeit.timeit(small_file)
        self.assertEquals(1, a)
'''

if __name__ == '__main__':
    name = "Synthetic"
    print("Starting testing")
    a = timeit.timeit(read_file, number=1)
    print(a)
    #a = timeit.timeit(copy_maps, number=1)
    print(a)
    #a = timeit.timeit(compare_maps, number=1)
    print(a)
    discretize()
    #a = timeit.timeit(discretize, number=1)
    print(a)
    print("Ended Testing")

