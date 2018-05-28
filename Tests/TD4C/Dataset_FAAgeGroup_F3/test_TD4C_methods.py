import csv
import unittest
from typing import Dict, List

from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.ClassicMethods.Persist import Persist
from Implementation.InputHandler import get_maps_from_file
from Implementation.TimeInterval import TimeInterval
from Implementation.TD4C.TD4C import TD4C
from Tests.Discretization_Result_Generator import get_test_result, assert_almost_equality
from Tests.Constants import DATASETS_PATH


class TestMethods(unittest.TestCase):
    DATASET_NAME = "FAAgeGroup_F3"
    CLASS_SEPERATOR = -1

    DATASET_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + ".csv"
    EXPECTED_OUTPUT_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + "_"
    PARTITIONS_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\partitions"
    ENTITIES_PATH = "%s\\%s\\%s" % (DATASETS_PATH, DATASET_NAME, "entities.csv")
    get_maps_from_file(DATASET_PATH, ENTITIES_PATH, CLASS_SEPERATOR)
    m1 = {}
    m2 = {}
    m3 = {}
    def test_EQW_3(self):
        d = EqualWidth(3,-1)
        d.property_folder = self.PARTITIONS_PATH
        name = "EQW3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_EQW_5(self):
        d = EqualWidth(5,-1)
        d.property_folder = self.PARTITIONS_PATH
        name = "EQW5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_Cos3(self):
        d = TD4C(3, TD4C.Cosine, -1)
        d.property_folder = self.PARTITIONS_PATH
        name = "TD4C_Cos3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_Cos5(self):
        d = TD4C(5, TD4C.Cosine, -1)
        d.property_folder = self.PARTITIONS_PATH
        name = "TD4C_Cos5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_Ent3(self):
        d = TD4C(3, TD4C.Entropy, -1)
        d.property_folder = self.PARTITIONS_PATH
        name = "TD4C_Ent3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_Ent5(self):
        d = TD4C(5, TD4C.Entropy, -1)
        d.property_folder = self.PARTITIONS_PATH
        name = "TD4C_Ent5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_KL3(self):
        d = TD4C(3, TD4C.KullbackLiebler, -1)
        d.property_folder = self.PARTITIONS_PATH
        name = "TD4C_KL3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_KL5(self):
        d = TD4C(5, TD4C.KullbackLiebler, -1)
        d.property_folder = self.PARTITIONS_PATH
        name = "TD4C_KL5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_Persist3(self):
        d = Persist(3, -1)
        d.property_folder = self.PARTITIONS_PATH
        name = "Persist3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_Persist5(self):
        d = Persist(5, -1)
        d.property_folder = self.PARTITIONS_PATH
        name = "Persist5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)


if __name__ == '__main__':
    unittest.main()

