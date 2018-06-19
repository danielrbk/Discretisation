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
    d = TD4C(5, "Cosine", 0, 1, ACCURACY_MEASURE=ACCURACY_MEASURE)
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
        expected = [25.8, 27.9, 15.0, 37.5]
        expected_scores = [0.5693783990540888, 0.5949977831555344, 0.631475034218052, 0.6916082623678628]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_td4c_property2(self):
        PROPERTY_ID = 2
        expected = [39.9, 18.9, 10.2, 20.1]
        expected_scores = [0.2334915838302562, 0.4636988090266874, 0.5095050256681237, 0.5694261099851294]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_td4c_property3(self):
        PROPERTY_ID = 3
        expected = [30.0, 40.0, 60.0, 40.2]
        expected_scores = [0.19419593704329513, 0.2584170907207789, 0.2651325373704161, 0.271042037116216]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_td4c_property4(self):
        PROPERTY_ID = 4
        expected = [35.0, 30.0, 21.0, 47.1]
        expected_scores = [0.5387112666909789, 0.6297703214966284, 0.6655443898656395, 0.6791193681056019]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_td4c_property5(self):
        PROPERTY_ID = 5
        expected = [40.05, 30.0, 159.9, 20.1]
        expected_scores = [0.22952910934155618, 0.35275248026189426, 0.3834998161941074, 0.4113392160794579]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_td4c_property6(self):
        PROPERTY_ID = 6
        expected = [37.33333333, 75.0, 60.0, 22.5]
        expected_scores = [0.14413764042777372, 0.2143343507307629, 0.2794901725501074, 0.36317265008882194]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_td4c_property39(self):
        PROPERTY_ID = 39
        expected = [7.0, 6.7, 7.34, 5.76]
        expected_scores = [0.832257936303481, 0.9004546956617143, 0.9869296103433957, 1.0543722116129388]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_td4c_property40(self):
        PROPERTY_ID = 40
        expected = [102.3, 131.0, 82.9, 115.0]
        expected_scores = [0.2496267127846074, 0.29095169547853567, 0.34442206078596227, 0.399363358960968]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_td4c_property41(self):
        PROPERTY_ID = 41
        expected = [207.0, 167.0, 193.0, 160.0]
        expected_scores = [0.2760339818416136, 0.33964116473114314, 0.39201971565342664, 0.40931253228030845]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_td4c_property42(self):
        PROPERTY_ID = 42
        expected = [136.0, 149.0, 101.0, 125.0]
        expected_scores = [0.604261190711666, 0.6719587584003983, 0.7876159067140891, 0.8230785156327413]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_td4c_property43(self):
        PROPERTY_ID = 43
        expected = [4.14, 4.29, 4.01, 4.32]
        expected_scores = [0.7271189486981469, 0.7998491723657154, 0.8255973459876492, 0.8721863895745438]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_td4c_property44(self):
        PROPERTY_ID = 44
        expected = [0.92, 1.01, 0.79, 1.1]
        expected_scores = [0.6380861304653831, 0.6723389522564095, 0.7371018539855466, 0.78591049444828]

        msg, res = test_td4c(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

if __name__ == '__main__':
    unittest.main()

