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
    d = TD4C(5, "Entropy", 0, 1, ACCURACY_MEASURE=ACCURACY_MEASURE)
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
        expected = [37.5, 52.5, 70.8, 40.8]
        expected_scores = [0.2647992304345539, 0.41638275817276305, 0.48865466340440666, 0.5574912896105875]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property2(self):
        PROPERTY_ID = 2
        expected = [39.9, 40.2, 59.85, 71.12]
        expected_scores = [0.24456052735390743, 0.34933296553174364, 0.4053134898347205, 0.4218584900361312]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property3(self):
        PROPERTY_ID = 3
        expected = [15.3, 30.0, 15.0, 22.5]
        expected_scores = [0.345243208871214, 0.4604391611856953, 0.5082931630546308, 0.5251477535124882]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property4(self):
        PROPERTY_ID = 4
        expected = [60.0, 77.0, 47.1, 90.0]
        expected_scores = [0.28663732693108446, 0.41978549560812994, 0.5296313514315207, 0.5962263974620716]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property5(self):
        PROPERTY_ID = 5
        expected = [20.1, 159.9, 15.0, 9.9]
        expected_scores = [0.21130763630793215, 0.29666343859708855, 0.35636849828459194, 0.355470269329877]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property6(self):
        PROPERTY_ID = 6
        expected = [15.0, 14.0, 60.0, 75.0]
        expected_scores = [0.14563737160575627, 0.17568457604043192, 0.17086941573742065, 0.18273483070350638]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property39(self):
        PROPERTY_ID = 39
        expected = [8.3, 10.5, 7.7, 8.82]
        expected_scores = [0.43670219810839006, 0.6491993119247526, 0.8263006994696587, 0.9316353917976339]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property40(self):
        PROPERTY_ID = 40
        expected = [140.2, 149.0, 58.0, 131.0]
        expected_scores = [0.15169234696598044, 0.2174127973840655, 0.2776570045466267, 0.32526349601445537]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property41(self):
        PROPERTY_ID = 41
        expected = [256.0, 219.0, 277.0, 230.0]
        expected_scores = [0.16496874642300113, 0.22182977799476822, 0.2636556371027554, 0.30432380519963553]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property42(self):
        PROPERTY_ID = 42
        expected = [193.0, 237.0, 170.0, 281.0]
        expected_scores = [0.44063332522212223, 0.5943362271860108, 0.7405010503793276, 0.8215507124465838]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property43(self):
        PROPERTY_ID = 43
        expected = [4.59, 4.43, 4.7, 4.32]
        expected_scores = [0.285143076397693, 0.39976758799141787, 0.49519035888987095, 0.560465440091924]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)

    def test_real_td4c_property44(self):
        PROPERTY_ID = 44
        expected = [1.3, 1.44, 1.2, 1.69]
        expected_scores = [0.4854526367770077, 0.6231051202113331, 0.7475556809294821, 0.8255781540959832]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res, msg)


if __name__ == '__main__':
    unittest.main()

