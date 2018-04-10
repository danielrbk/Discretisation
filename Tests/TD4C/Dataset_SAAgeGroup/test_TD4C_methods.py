import csv
import unittest
from typing import Dict, List

from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.ClassicMethods.Persist import Persist
from Implementation.DataObject import DataObject
from Implementation.InputHandler import get_maps_from_file
from Implementation.TimeInterval import TimeInterval
from Implementation.TD4C.TD4C import TD4C
from Tests.Discretization_Result_Generator import get_test_result, assert_almost_equality
from Tests.Constants import DATASETS_PATH


class TestMethods(unittest.TestCase):
    DATASET_NAME = "SAAgeGroup"
    CLASS_SEPERATOR = 55

    DATASET_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + ".csv"
    EXPECTED_OUTPUT_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + "_"
    m1, m2, m3 = get_maps_from_file(DATASET_PATH, CLASS_SEPERATOR)

    def test_EQW_3(self):
        d = EqualWidth(3)
        name = "EQW3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_EQW_5(self):
        d = EqualWidth(5)
        name = "EQW5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_Cos3(self):
        d = TD4C(3, TD4C.Cosine)
        name = "TD4C_Cos3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_Cos5(self):
        d = TD4C(5, TD4C.Cosine)
        name = "TD4C_Cos5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_Ent3(self):
        d = TD4C(3, TD4C.Entropy)
        name = "TD4C_Ent3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_Ent5(self):
        d = TD4C(5, TD4C.Entropy)
        name = "TD4C_Ent5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_KL3(self):
        d = TD4C(3, TD4C.KullbackLiebler)
        name = "TD4C_KL3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_TD4C_KL5(self):
        d = TD4C(5, TD4C.KullbackLiebler)
        name = "TD4C_KL5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_Persist3(self):
        d = Persist(3)
        name = "Persist3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Dataset_Persist5(self):
        d = Persist(5)
        name = "Persist5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_Cos5(self):
        d = TD4C(5, TD4C.Cosine)
        name = "Old_TD4C_Cos5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_Ent5(self):
        d = TD4C(5, TD4C.Entropy)
        name = "Old_TD4C_Ent5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_KL5(self):
        d = TD4C(5, TD4C.KullbackLiebler)
        name = "Old_TD4C_KL5"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_Cos4(self):
        d = TD4C(4, TD4C.Cosine)
        name = "Old_TD4C_Cos4"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_Ent4(self):
        d = TD4C(4, TD4C.Entropy)
        name = "Old_TD4C_Ent4"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_KL4(self):
        d = TD4C(4, TD4C.KullbackLiebler)
        name = "Old_TD4C_KL4"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_Cos3(self):
        d = TD4C(3, TD4C.Cosine)
        name = "Old_TD4C_Cos3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_Ent3(self):
        d = TD4C(3, TD4C.Entropy)
        name = "Old_TD4C_Ent3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_KL3(self):
        d = TD4C(3, TD4C.KullbackLiebler)
        name = "Old_TD4C_KL3"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_Cos2(self):
        d = TD4C(2, TD4C.Cosine)
        name = "Old_TD4C_Cos2"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_Ent2(self):
        d = TD4C(2, TD4C.Entropy)
        name = "Old_TD4C_Ent2"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_Raw_TD4C_KL2(self):
        d = TD4C(2, TD4C.KullbackLiebler)
        name = "Old_TD4C_KL2"

        path = self.EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)




if __name__ == '__main__':
    unittest.main()

