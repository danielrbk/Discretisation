import csv
import unittest
from typing import Dict, List

from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.ClassicMethods.Persist import Persist
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


def generate_cutpoints(min, max, bins):
    interval = (max-min)/bins
    return [min + i*interval for i in range(1,bins)]


def test_cutpoints(MAX, MIN, PROPERTY_ID):
    res = True
    msg = ""
    m1 = {}
    m2 = {}
    m3 = {}
    for c in range(2, 1000):
        d = EqualWidth(c, 0)
        d.property_folder = PARTITIONS_PATH
        expected_cutpoints = {PROPERTY_ID: generate_cutpoints(MIN, MAX, c)}
        d.discretize_property_without_abstracting(m1, m2, m3, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        t_res, t_msg = assert_almost_equality(expected_cutpoints, real_cutpoints)
        res &= t_res
        msg += t_msg
    return msg, res


class TestMethods(unittest.TestCase):
    def test_synthetic_EQW_2(self):
        d = EqualWidth(2, 0)
        p2t = {1:[]}
        p2t[1] = [TimeStamp(-75,1,1,0),TimeStamp(25,1,1,0)] # min = -75, max = 25
        expected_cutpoints = {1:[-25]}
        d.discretize_property_without_abstracting({},{},p2t,1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints,real_cutpoints)
        self.assertTrue(res,msg)

    def test_synthetic_EQW_3(self):
        d = EqualWidth(3, 0)
        p2t = {1: []}
        p2t[1] = [TimeStamp(-75, 1, 1, 0), TimeStamp(25, 1, 1, 0)]  # min = -75, max = 25
        expected_cutpoints = {1: [-75 + 100/3, -75 + 200/3]}
        d.discretize_property_without_abstracting({}, {}, p2t, 1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)
        self.assertTrue(res, msg)

    def test_synthetic_EQW_4(self):
        d = EqualWidth(4, 0)
        p2t = {1: []}
        p2t[1] = [TimeStamp(-75, 1, 1, 0), TimeStamp(25, 1, 1, 0)]  # min = -75, max = 25
        expected_cutpoints = {1: [-50,-25,0]}
        d.discretize_property_without_abstracting({}, {}, p2t, 1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)
        self.assertTrue(res, msg)

    def test_synthetic_EQW_5(self):
        d = EqualWidth(5, 0)
        p2t = {1: []}
        p2t[1] = [TimeStamp(-75, 1, 1, 0), TimeStamp(25, 1, 1, 0)]  # min = -75, max = 25
        expected_cutpoints = {1: [-55,-35,-15,5]}
        d.discretize_property_without_abstracting({}, {}, p2t, 1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)
        self.assertTrue(res, msg)

    def test_synthetic_stress_EQW_2(self):
        d = EqualWidth(2, 0)
        p2t = {1:[]}
        p2t[1] = [TimeStamp(3, 1, 1, 0)] * STRESS_VALUE_COUNT + [TimeStamp(-75, 1, 1, 0)] + [TimeStamp(3, 1, 1,
                                                                                                       0)] * STRESS_VALUE_COUNT + [
                     TimeStamp(25, 1, 1, 0)] + [TimeStamp(3, 1, 1, 0)] * STRESS_VALUE_COUNT  # min = -75, max = 25
        expected_cutpoints = {1:[-25]}
        d.discretize_property_without_abstracting({},{},p2t,1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints,real_cutpoints)
        self.assertTrue(res,msg)

    def test_synthetic_stress_EQW_3(self):
        d = EqualWidth(3, 0)
        p2t = {1: []}
        p2t[1] = [TimeStamp(3, 1, 1, 0)] * STRESS_VALUE_COUNT + [TimeStamp(-75, 1, 1, 0)] + [TimeStamp(3, 1, 1,
                                                                                                       0)] * STRESS_VALUE_COUNT + [
                     TimeStamp(25, 1, 1, 0)] + [TimeStamp(3, 1, 1, 0)] * STRESS_VALUE_COUNT  # min = -75, max = 25
        expected_cutpoints = {1: [-75 + 100/3, -75 + 200/3]}
        d.discretize_property_without_abstracting({}, {}, p2t, 1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)
        self.assertTrue(res, msg)

    def test_synthetic_stress_EQW_4(self):
        d = EqualWidth(4, 0)
        p2t = {1: []}
        p2t[1] = [TimeStamp(3, 1, 1, 0)] * STRESS_VALUE_COUNT + [TimeStamp(-75, 1, 1, 0)] + [TimeStamp(3, 1, 1,
                                                                                                       0)] * STRESS_VALUE_COUNT + [
                     TimeStamp(25, 1, 1, 0)] + [TimeStamp(3, 1, 1, 0)] * STRESS_VALUE_COUNT  # min = -75, max = 25
        expected_cutpoints = {1: [-50,-25,0]}
        d.discretize_property_without_abstracting({}, {}, p2t, 1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)
        self.assertTrue(res, msg)

    def test_synthetic_stress_EQW_5(self):
        d = EqualWidth(5, 0)
        p2t = {1: []}
        p2t[1] = [TimeStamp(3, 1, 1, 0)] * STRESS_VALUE_COUNT + [TimeStamp(-75, 1, 1, 0)] + [TimeStamp(3, 1, 1,
                                                                                                       0)] * STRESS_VALUE_COUNT + [
                     TimeStamp(25, 1, 1, 0)] + [TimeStamp(3, 1, 1, 0)] * STRESS_VALUE_COUNT  # min = -75, max = 25
        expected_cutpoints = {1: [-55,-35,-15,5]}
        d.discretize_property_without_abstracting({}, {}, p2t, 1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)
        self.assertTrue(res, msg)

    def test_syntetic_cutpoint_generation(self):
        res = True
        msg = ""
        for c in range(2,1000):
            d = EqualWidth(c,0)
            p2t = {1: []}
            p2t[1] = [TimeStamp(-75, 1, 1, 0), TimeStamp(25, 1, 1, 0)]  # min = -75, max = 25
            interval = 100/c
            expected_cutpoints = {1: [-75+interval*i for i in range(1,c)]}
            d.discretize_property_without_abstracting({}, {}, p2t, 1)
            real_cutpoints = d.bins_cutpoints
            t_res, t_msg = assert_almost_equality(expected_cutpoints, real_cutpoints)
            res &= t_res
            msg += t_msg
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_1(self):
        MIN = 0.43
        MAX = 242.4
        PROPERTY_ID = 1
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_2(self):
        MIN = 0.33
        MAX = 239.4
        PROPERTY_ID = 2
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_3(self):
        MIN = 1
        MAX = 240
        PROPERTY_ID = 3
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_4(self):
        MIN = 0.5
        MAX = 377.2
        PROPERTY_ID = 4
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_5(self):
        MIN = 0.67
        MAX = 500.1
        PROPERTY_ID = 5
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_6(self):
        MIN = 2.5
        MAX = 373.52
        PROPERTY_ID = 6
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_39(self):
        MIN = 3.9
        MAX = 222.7
        PROPERTY_ID = 39
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_40(self):
        MIN = 2.8
        MAX = 328.39999
        PROPERTY_ID = 40
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_41(self):
        MIN = 64
        MAX = 557
        PROPERTY_ID = 41
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_42(self):
        MIN = 28
        MAX = 802
        PROPERTY_ID = 42
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_43(self):
        MIN = 2
        MAX = 5.8
        PROPERTY_ID = 43
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)

    def test_EQW_FAAgeGroup_F3_Property_44(self):
        MIN = 0.28
        MAX = 11.8
        PROPERTY_ID = 44
        msg, res = test_cutpoints(MAX, MIN, PROPERTY_ID)
        self.assertTrue(res, msg)




if __name__ == '__main__':
    unittest.main()

