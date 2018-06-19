import csv
import unittest
from typing import Dict, List

import numpy as np

from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.ClassicMethods.Persist import Persist
from Implementation.Entity import Entity
from Implementation.InputHandler import get_maps_from_file
from Implementation.TimeInterval import TimeInterval
from Implementation.TD4C.TD4C import TD4C
from Implementation.TimeStamp import TimeStamp
from Tests.Discretization_Result_Generator import get_test_result, assert_almost_equality
from Tests.Constants import DATASETS_PATH, STRESS_VALUE_COUNT

DATASET_NAME = "FAAgeGroup_F3"
CLASS_SEPERATOR = -1

DATASET_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + ".csv"
EXPECTED_OUTPUT_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + "_"
PARTITIONS_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\partitions"
ENTITIES_PATH = "%s\\%s\\%s" % (DATASETS_PATH, DATASET_NAME, "entities.csv")
get_maps_from_file(DATASET_PATH, ENTITIES_PATH, CLASS_SEPERATOR)


def test_td4c(PROPERTY_ID, expected, expected_scores):
    ACCURACY_MEASURE = 100
    res_bool = True
    msg = ""
    d = TD4C(5, "KullbackLiebler", 0, 1, ACCURACY_MEASURE=ACCURACY_MEASURE)
    d.property_folder = PARTITIONS_PATH
    p2t = {}
    d.load_property_to_timestamps(p2t, PROPERTY_ID)
    d.discretize_property_without_abstracting({}, {}, p2t, PROPERTY_ID)
    res = d.cutoffs_according_to_order
    res_scores = d.chosen_scores
    t_res, t_msg = assert_almost_equality({PROPERTY_ID: expected}, res)
    if not t_res:
        msg += "\nCutoffs wrong!\n%s\n" % t_msg
        res_bool = False
    t_res, t_msg = assert_almost_equality({PROPERTY_ID: expected_scores}, res_scores)
    if not t_res:
        msg += "\nScores wrong!\n%s\n" % t_msg
        res_bool = False
    return msg, res_bool


class TestMethods(unittest.TestCase):
    def test_real_td4c_property1(self):
        PROPERTY_ID = 1
        expected = [25.8, 52.5, 15.0, 12.9]
        expected_scores = [0.06365727886095762, 0.08116792130512952, 0.09578781259718411, 0.11470821865706246]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property2(self):
        PROPERTY_ID = 2
        expected = [39.9, 38.1, 9.9, 7.5]
        expected_scores = [0.038244817392141375, 0.0635223102192988, 0.08915061852514651, 0.10849458221847205]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property3(self):
        PROPERTY_ID = 3
        expected = [20.0, 15.3, 15.0, 11.7]
        expected_scores = [0.08337991020260296, 0.10059145084980599, 0.11988952769930385, 0.14274699741855507]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property4(self):
        PROPERTY_ID = 4
        expected = [47.1, 21.0, 8.62, 22.5]
        expected_scores = [0.07802205644031282, 0.08447900231628691, 0.10176997908058438, 0.11104748437745704]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property5(self):
        PROPERTY_ID = 5
        expected = [20.1, 40.05, 159.9, 90.0]
        expected_scores = [0.027354919827951584, 0.04063188265919058, 0.05260315384690769, 0.06152869592264801]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property6(self):
        PROPERTY_ID = 6
        expected = [15.0, 14.0, 112.0, 60.0]
        expected_scores = [0.014239082328194454, 0.049174172459255615, 0.059980740289417564, 0.07124263153339203]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property39(self):
        PROPERTY_ID = 39
        expected = [7.6, 10.5, 6.7, 8.82]
        expected_scores = [0.1748731928819994, 0.21844158044890066, 0.23983946058704722, 0.24712947860219545]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property40(self):
        PROPERTY_ID = 40
        expected = [131.0, 46.0, 161.0, 132.20399980000082]
        expected_scores = [0.018406723764553254, 0.024218848793171804, 0.028064693767656357, 0.031809125778531705]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property41(self):
        PROPERTY_ID = 41
        expected = [207.0, 252.0, 164.0, 199.0]
        expected_scores = [0.01943086837806923, 0.028292200341950378, 0.03209961267217668, 0.03727953633096156]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property42(self):
        PROPERTY_ID = 42
        expected = [170.0, 136.0, 197.0, 89.0]
        expected_scores = [0.1272903396424802, 0.13914616676206706, 0.14986278676192635, 0.15563654329803941]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property43(self):
        PROPERTY_ID = 43
        expected = [4.14, 4.59, 4.01, 4.06]
        expected_scores = [0.11043030371481008, 0.12403433209033214, 0.13234028263683315, 0.1440701013652282]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property44(self):
        PROPERTY_ID = 44
        expected = [1.3, 0.92, 1.2, 1.09]
        expected_scores = [0.13152055208186608, 0.16506661219851623, 0.17168388796716377, 0.17510574199655804]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)


if __name__ == '__main__':
    unittest.main()

