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


def test_persist(PROPERTY_ID, expected, expected_scores):
    ACCURACY_MEASURE = 100
    res_bool = True
    msg = ""
    d = Persist(5, 0, 1, ACCURACY_MEASURE=ACCURACY_MEASURE)
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

    def test_collapse_matrix_one_cutpoint(self):
        A = [[0, 1, 0, 0],
             [2, 0, 0, 0],
             [0, 1, 2, 0],
             [0, 0, 1, 1]]
        A = np.array(A)
        res = np.array([[6,0],
                        [1,1]])
        cutpoints = [2]

        self.assertEqual(res.tolist(), Persist.collapse_matrix(A, cutpoints).tolist(), "Collapse failed with one cutpoint")

    def test_collapse_matrix_two_cutpoints(self):
        A = [[0, 1, 0, 0],
             [2, 0, 0, 0],
             [0, 1, 2, 0],
             [0, 0, 1, 1]]
        A = np.array(A)
        res = np.array([[3,0,0],
                        [1,2,0],
                        [0,1,1]])
        cutpoints = [1,2]

        self.assertEqual(res.tolist(), Persist.collapse_matrix(A, cutpoints).tolist(), "Collapse failed with two cutpoints")

    def test_collapse_matrix_three_cutpoints(self):
        A = [[0, 1, 0, 0],
             [2, 0, 0, 0],
             [0, 1, 2, 0],
             [0, 0, 1, 1]]
        A = np.array(A)
        res = A
        cutpoints = [0,1,2]

        self.assertEqual(res.tolist(), Persist.collapse_matrix(A, cutpoints).tolist(), "Collapse failed with three cutpoints")

    def test_load_state_information(self):
        time_series = [TimeStamp(0, 1, 1, 0), TimeStamp(1, 1, 1, 0),
                      TimeStamp(2, 1, 1, 0), TimeStamp(2, 1, 1, 0),
                      TimeStamp(1, 1, 1, 0), TimeStamp(1, 1, 1, 0),
                      TimeStamp(2, 1, 1, 0), TimeStamp(1, 1, 1, 0),
                      TimeStamp(1, 1, 1, 0), TimeStamp(1, 1, 1, 0)]
        expected_A = [[0, 0, 0],
                      [1, 3, 2],
                      [0, 2, 1]]
        expected_state_vector = [1,6,3]
        state_count = 3
        A = np.zeros(shape=(state_count, state_count))
        state_vector = [0]*state_count
        e = Entity(0,0)
        e.properties = {1:time_series}
        Persist.load_state_information(A,1,{1:{e}},state_vector)
        res = True
        msg = ""
        A = A.tolist()
        if A != expected_A:
            res = False
            msg += "Collapsed matrices different. Expected: %s, Got: %s\n" % (expected_A,A)
        if state_vector != expected_state_vector:
            res = False
            msg += "State count vectors different. Expected: %s, Got: %s\n" % (expected_state_vector, state_vector)
        self.assertTrue(res,msg)

    def test_real_persist_property1(self):
        PROPERTY_ID = 1
        expected = [10, 12.9, 11.7, 15]
        expected_scores = [3.36353515, 2.64247706, 2.36769129, 2.1590023]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_persist_property2(self):
        PROPERTY_ID = 2
        expected = [ 5.1, 6.6, 20.1, 22.8888]
        expected_scores = [3.81267604, 3.30891564, 2.92647525, 2.71796233]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_persist_property3(self):
        PROPERTY_ID = 3
        expected = [15, 15.3, 20, 22.5]
        expected_scores = [3.91737716, 3.02430198, 2.75574736, 2.69082414]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_persist_property4(self):
        PROPERTY_ID = 4
        expected = [8.62, 20, 28, 22.5 ]
        expected_scores = [3.49251506, 2.60362733, 2.2655962, 1.99209887]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_persist_property5(self):
        PROPERTY_ID = 5
        expected = [15, 20.1, 159.9, 100.2]
        expected_scores = [5.01788008, 3.7998274,  2.74445189, 2.23635882]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_persist_property6(self):
        PROPERTY_ID = 6
        expected = [14, 15, 28, 18.76]
        expected_scores = [3.91205355, 3.05042887, 2.31287697, 2.37240622]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_persist_property39(self):
        PROPERTY_ID = 39
        expected = [5, 5.2, 5.3, 5.4]
        expected_scores = [4.81654649, 4.20170153, 3.93668389, 3.78119058]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_persist_property40(self):
        PROPERTY_ID = 40
        expected = [46, 54, 196, 184]
        expected_scores = [4.38201031, 3.7779907,  3.49002935, 3.35392952]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_persist_property41(self):
        PROPERTY_ID = 41
        expected = [114, 308, 123, 135]
        expected_scores = [4.29979921, 3.71540622, 3.41703894, 3.26314693]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_persist_property42(self):
        PROPERTY_ID = 42
        expected = [78, 76, 83, 82]
        expected_scores = [4.10237025, 3.68461124, 3.46570155, 3.31676202]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_persist_property43(self):
        PROPERTY_ID = 43
        expected = [4.9, 4.8, 3.8, 3.77]
        expected_scores = [4.45951486, 3.90046647, 3.61273054, 3.53815866]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

    def test_real_persist_property44(self):
        PROPERTY_ID = 44
        expected = [0.48, 1.95, 1.33, 0.75]
        expected_scores = [4.44787821, 3.91327717, 3.62288248, 3.51455014]

        msg, res = test_persist(PROPERTY_ID, expected, expected_scores)

        self.assertTrue(res,msg)

if __name__ == '__main__':
    unittest.main()

