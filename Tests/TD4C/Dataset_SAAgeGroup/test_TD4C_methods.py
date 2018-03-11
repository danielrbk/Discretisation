import csv
import unittest
from typing import Dict, List

from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.DataObject import DataObject
from Implementation.InputHandler import get_maps_from_file
from Implementation.TimeInterval import TimeInterval
from Implementation.TD4C import TD4C
from Tests.Discretization_Result_Generator import get_test_result
from Tests.Constants import DATASETS_PATH

DATASET_NAME = "SAAgeGroup"
CLASS_SEPERATOR = 55

DATASET_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + ".csv"
EXPECTED_OUTPUT_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + "_"


class TestMethods(unittest.TestCase):
    def test_EQW_3(self):
        d = EqualWidth(3)
        name = "EQW3"

        m1, m2, m3 = get_maps_from_file(DATASET_PATH, CLASS_SEPERATOR)
        path = EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, m1, m2, m3, d)
        self.assertEquals(real, expected)

    def test_EQW_5(self):
        d = EqualWidth(5)
        name = "EQW5"

        m1, m2, m3 = get_maps_from_file(DATASET_PATH, CLASS_SEPERATOR)
        path = EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, m1, m2, m3, d)
        self.assertEquals(real, expected)


if __name__ == '__main__':
    unittest.main()

