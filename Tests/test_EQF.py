import csv
import unittest
from typing import Dict, List

from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.ClassicMethods.Persist import Persist
from Implementation.Constants import EPSILON
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


class TestMethods(unittest.TestCase):

    def test_synthetic_EQF_array_partial_index_0(self):
        test_arr = [-1,0,1]
        res = EqualFrequency.get_cutpoint(0, test_arr)
        expected = -1 + EPSILON
        self.assertAlmostEqual(expected,res)

    def test_synthetic_EQF_array_partial_index_half(self):
        test_arr = [-1, 0, 1]
        res = EqualFrequency.get_cutpoint(1/2, test_arr)
        expected = -1/2
        self.assertAlmostEqual(expected, res)

    def test_synthetic_EQF_array_partial_index_1(self):
        test_arr = [-1, 0, 1]
        res = EqualFrequency.get_cutpoint(1, test_arr)
        expected = 0 + EPSILON
        self.assertAlmostEqual(expected, res)

    def test_synthetic_EQF_array_partial_index_1_half(self):
        test_arr = [-1, 0, 1]
        res = EqualFrequency.get_cutpoint(3/2, test_arr)
        expected = 1/2
        self.assertAlmostEqual(expected, res)

    def test_synthetic_EQF_array_partial_index_2(self):
        test_arr = [-1, 0, 1]
        res = EqualFrequency.get_cutpoint(2-EPSILON, test_arr)
        expected = 1
        self.assertAlmostEqual(expected, res)

    def test_synthetic_EQF_2(self):
        d = EqualFrequency(2, 0)
        p2t = {1:[]}
        p2t[1] = [TimeStamp(-75,1,1,0),TimeStamp(25,1,1,0)] # min = -75, max = 25
        expected_cutpoints = {1:[-25]}
        d.discretize_property_without_abstracting({},{},p2t,1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints,real_cutpoints)
        self.assertTrue(res,msg)

    def test_synthetic_EQF_3(self):
        d = EqualFrequency(3, 0)
        p2t = {1:[]}
        p2t[1] = [TimeStamp(-75,1,1,0),TimeStamp(25,1,1,0)] # min = -75, max = 25
        expected_cutpoints = {1:[-75+100/3,-75+200/3]}
        d.discretize_property_without_abstracting({},{},p2t,1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints,real_cutpoints)
        self.assertTrue(res,msg)

    def test_synthetic_EQF_4(self):
        d = EqualFrequency(4, 0)
        p2t = {1:[]}
        p2t[1] = [TimeStamp(-75,1,1,0),TimeStamp(25,1,1,0)] # min = -75, max = 25
        expected_cutpoints = {1:[-50,-25,0]}
        d.discretize_property_without_abstracting({},{},p2t,1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints,real_cutpoints)
        self.assertTrue(res,msg)

    def test_synthetic_EQF_5(self):
        d = EqualFrequency(5, 0)
        p2t = {1:[]}
        p2t[1] = [TimeStamp(-75,1,1,0),TimeStamp(25,1,1,0)] # min = -75, max = 25
        expected_cutpoints = {1:[-55,-35,-15,5]}
        d.discretize_property_without_abstracting({},{},p2t,1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints,real_cutpoints)
        self.assertTrue(res,msg)

    def test_synthetic_EQF_Stress_Many_Requests(self):
        res = True
        msg = ""
        p2t = {1: [TimeStamp(0,1,1,0),TimeStamp(1,1,1,0)]}
        for bin_count in range(2,10000):
            d = EqualFrequency(bin_count, 0)
            d.discretize_property_without_abstracting({},{},p2t,1)
            sum_real_cutpoints = sum(d.bins_cutpoints[1])
            expected_sum = (bin_count-1)/2
            t_res, t_msg = assert_almost_equality({1:[expected_sum]}, {1:[sum_real_cutpoints]})
            res &= t_res
            msg += t_msg
        self.assertTrue(res,msg)

    def test_synthetic_EQF_Stress_Big_Request_2(self):
        p2t = {1: [TimeStamp(i,1,1,0) for i in range(STRESS_VALUE_COUNT)]}
        max_index = STRESS_VALUE_COUNT - 1
        BIN_COUNT = 2
        d = EqualFrequency(BIN_COUNT, 0)
        d.discretize_property_without_abstracting({}, {}, p2t, 1)
        expected_res = {1: [i * max_index / BIN_COUNT for i in range(1, BIN_COUNT)]}
        res = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_res,res)
        self.assertTrue(res,msg)

    def test_synthetic_EQF_Stress_Big_Request_3(self):
        p2t = {1: [TimeStamp(i,1,1,0) for i in range(STRESS_VALUE_COUNT)]}
        max_index = STRESS_VALUE_COUNT - 1
        BIN_COUNT = 3
        d = EqualFrequency(BIN_COUNT, 0)
        d.discretize_property_without_abstracting({}, {}, p2t, 1)
        expected_res = {1: [i * max_index / BIN_COUNT for i in range(1, BIN_COUNT)]}
        res = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_res,res)
        self.assertTrue(res,msg)

    def test_synthetic_EQF_Stress_Big_Request_4(self):
        p2t = {1: [TimeStamp(i,1,1,0) for i in range(STRESS_VALUE_COUNT)]}
        max_index = STRESS_VALUE_COUNT - 1
        BIN_COUNT = 4
        d = EqualFrequency(BIN_COUNT, 0)
        d.discretize_property_without_abstracting({}, {}, p2t, 1)
        expected_res = {1:[i*max_index/BIN_COUNT for i in range(1,BIN_COUNT)]}
        res = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_res,res)
        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_1(self):
        PROPERTY_ID = 1
        EXPECTED_RES = [12.9,15,25.8,38.7]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_2(self):
        PROPERTY_ID = 2
        EXPECTED_RES = [9.9,19.8,20.1,35.56]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_3(self):
        PROPERTY_ID = 3
        EXPECTED_RES = [30,60]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_4(self):
        PROPERTY_ID = 4
        EXPECTED_RES = [28,30,58]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_5(self):
        PROPERTY_ID = 5
        EXPECTED_RES = [20.1,39.9,53.4]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_6(self):
        PROPERTY_ID = 6
        EXPECTED_RES = [22.5,30,56,60]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_39(self):
        PROPERTY_ID = 39
        EXPECTED_RES = [6.1,6.6,7.2,8.1]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_40(self):
        PROPERTY_ID = 40
        EXPECTED_RES = [83.8,99.4,115,136]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_41(self):
        PROPERTY_ID = 41
        EXPECTED_RES = [160,181,201,226]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_42(self):
        PROPERTY_ID = 42
        EXPECTED_RES = [99,119,139,170]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_43(self):
        PROPERTY_ID = 43
        EXPECTED_RES = [3.9,4.1,4.3,4.5]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

    def test_real_EQF_FAAgeGroup_F3_Property_44(self):
        PROPERTY_ID = 44
        EXPECTED_RES = [0.71,0.84,0.95,1.1]

        d = EqualFrequency(5, 0)
        d.property_folder = PARTITIONS_PATH
        d.discretize_property_without_abstracting({}, {}, {}, PROPERTY_ID)
        real_cutpoints = d.bins_cutpoints
        expected_cutpoints = {PROPERTY_ID: EXPECTED_RES}
        res, msg = assert_almost_equality(expected_cutpoints, real_cutpoints)

        self.assertTrue(res,msg)

if __name__ == '__main__':
    unittest.main()

