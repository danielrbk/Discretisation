import csv
import timeit
import unittest
from typing import Dict, List

from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.DataObject import DataObject
from Implementation.InputHandler import get_maps_from_file
from Implementation.TimeInterval import TimeInterval
from Implementation.TD4C.TD4C import TD4C
from Tests.Discretization_Result_Generator import get_test_result
from Tests.Constants import DATASETS_PATH

DATASET_NAME = "SAGender"
CLASS_SEPERATOR = 55

DATASET_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + ".csv"
EXPECTED_OUTPUT_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + "_"


def small_file():
    d = TD4C(5,TD4C.Cosine)
    print("Reading file...")
    m1, m2, m3 = get_maps_from_file(DATASET_PATH, CLASS_SEPERATOR)
    print("Discretizing...")
    r1,r2,r3 = d.discretize(m1,m2,m3)


'''
class TimingTest(unittest.TestCase):
    def test_small_file_read(self):
        d = EqualWidth(3)
        name = "EQW3"
        a = timeit.timeit(small_file)
        self.assertEquals(1, a)
'''

if __name__ == '__main__':
    print("Starting testing")
    a = timeit.timeit(small_file, number=1)
    print(a)
    print("Ended Testing")
