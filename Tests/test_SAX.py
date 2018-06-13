import csv
import unittest
from functools import reduce
from typing import Dict, List

from numpy import mean

from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.ClassicMethods.Persist import Persist
from Implementation.ClassicMethods.SAX import SaxConstrainsException, __SAX__, SAX
from Implementation.InputHandler import get_maps_from_file
from Implementation.TimeInterval import TimeInterval
from Implementation.TD4C.TD4C import TD4C
from Implementation.TimeStamp import TimeStamp
from Tests.Discretization_Result_Generator import get_test_result, assert_almost_equality, compare_time_stamps
from Tests.Constants import DATASETS_PATH, STRESS_VALUE_COUNT

DATASET_NAME = "FAAgeGroup_F3"
CLASS_SEPERATOR = -1

DATASET_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + ".csv"
EXPECTED_OUTPUT_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + "_"
PARTITIONS_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\partitions"
ENTITIES_PATH = "%s\\%s\\%s" % (DATASETS_PATH, DATASET_NAME, "entities.csv")
get_maps_from_file(DATASET_PATH, ENTITIES_PATH, CLASS_SEPERATOR)


def test_SAX(MEAN, STD, PROPERTY_ID):
    msg = ""
    for BIN_COUNT in range(2,6):
        for WINDOW_SIZE in range(2,6):
            d = SAX(BIN_COUNT, -1, WINDOW_SIZE)
            d.property_folder = PARTITIONS_PATH
            limits = __SAX__.build_limits(BIN_COUNT)
            p2t = {}
            d.load_property_to_timestamps(p2t, PROPERTY_ID)
            _,_,d_p2t = d.discretize_property({}, {}, p2t, PROPERTY_ID)
            values = [(ts.value - MEAN) / STD for ts in p2t[PROPERTY_ID]]
            length = len(values) // WINDOW_SIZE
            remainder = len(values) % WINDOW_SIZE
            found = True
            reduced_vals = []
            x = 0
            for i in range(0, length):
                reduced_vals.append(mean(values[i * WINDOW_SIZE:(i + 1) * WINDOW_SIZE]))
            if remainder != 0:
                reduced_vals.append(mean(values[length * WINDOW_SIZE:length * WINDOW_SIZE + remainder]))
            for i in range(len(reduced_vals)):
                val = reduced_vals[i]
                found = False
                for j in range(len(limits)):
                    if val <= limits[j]:
                        reduced_vals[i] = j
                        found = True
                        break
                if not found:
                    reduced_vals[i] = len(limits)

            if remainder == 0:
                rng = range(len(reduced_vals))
            else:
                rng = range(len(reduced_vals) - 1)
            for i in rng:
                val = reduced_vals[i]
                for j in range(WINDOW_SIZE):
                    values[i * WINDOW_SIZE + j] = val
            for i in range(remainder):
                values[(len(reduced_vals) - 1) * WINDOW_SIZE + i] = reduced_vals[-1]

            tss = p2t[PROPERTY_ID]
            for i in range(len(values)):
                tss[i].value = values[i]

            t_msg = compare_time_stamps(p2t,d_p2t)
            if t_msg != "":
                msg += "\nBIN COUNT - %s. WINDOW SIZE - %s\n------------\n" % (BIN_COUNT, WINDOW_SIZE) + t_msg
    return msg


class TestMethods(unittest.TestCase):

    def test_SAX_mechanics_normalize_no_std(self):
        d = __SAX__()
        vals = [10] * STRESS_VALUE_COUNT

        with self.assertRaises(SaxConstrainsException, msg="No standard deviation not caught"):
            d.normalize(vals)

    def test_SAX_mechanics_normalize_std(self):
        d = __SAX__()
        vals = [i for i in range(100)]
        mean = 49.5
        std = 28.86607005
        normalized_vals = [(i-mean)/std for i in vals]
        real_vals = d.normalize(vals)
        res, msg = assert_almost_equality({1:normalized_vals},{1:real_vals})
        self.assertTrue(res,msg)

    def test_SAX_mechanics_PAA_identical(self):
        d = __SAX__(points_amount=3)
        vals = reduce(lambda x,y: x + y,[[i,i,i] for i in range(100)])
        expected = list(range(100))
        real, _ = d.to_paa(vals)
        res, msg = assert_almost_equality({1: expected}, {1: list(real)})
        self.assertTrue(res, msg)

    def test_SAX_mechanics_PAA_mean(self):
        d = __SAX__(points_amount=3)
        vals = reduce(lambda x,y: x + y,[[i-1,i,i+1] for i in range(100)])
        expected = list(range(100))
        real, _ = d.to_paa(vals)
        res, msg = assert_almost_equality({1: expected}, {1: list(real)})
        self.assertTrue(res, msg)

    def test_SAX_mechanics_PAA_extras(self):
        d = __SAX__(points_amount=3)
        vals = reduce(lambda x,y: x + y,[[i,i,i] for i in range(100)]) + [1000,1002]
        expected = list(range(100)) + [1001]
        real, _ = d.to_paa(vals)
        res, msg = assert_almost_equality({1: expected}, {1: list(real)})
        self.assertTrue(res, msg)

    def test_SAX_FAAgeGroup_F3_Property_1(self):
        MEAN = 26.48799128
        STD = 17.67323318
        PROPERTY_ID = 1
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)

    def test_SAX_FAAgeGroup_F3_Property_2(self):
        MEAN = 22.23111677
        STD = 13.32752946
        PROPERTY_ID = 2
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)

    def test_SAX_FAAgeGroup_F3_Property_3(self):
        MEAN = 37.05087526
        STD = 17.45487494
        PROPERTY_ID = 3
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)

    def test_SAX_FAAgeGroup_F3_Property_4(self):
        MEAN = 41.2967445
        STD = 25.14178844
        PROPERTY_ID = 4
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)

    def test_SAX_FAAgeGroup_F3_Property_5(self):
        MEAN = 42.28291332
        STD = 27.53388945
        PROPERTY_ID = 5
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)

    def test_SAX_FAAgeGroup_F3_Property_6(self):
        MEAN = 48.93639578
        STD = 35.76889116
        PROPERTY_ID = 6
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)

    def test_SAX_FAAgeGroup_F3_Property_39(self):
        MEAN = 7.314621419
        STD = 3.962026697
        PROPERTY_ID = 39
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)

    def test_SAX_FAAgeGroup_F3_Property_40(self):
        MEAN = 110.2362273
        STD = 32.07542885
        PROPERTY_ID = 40
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)

    def test_SAX_FAAgeGroup_F3_Property_41(self):
        MEAN = 194.5167596
        STD = 40.70264974
        PROPERTY_ID = 41
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)

    def test_SAX_FAAgeGroup_F3_Property_42(self):
        MEAN = 140.8245102
        STD = 54.33412773
        PROPERTY_ID = 42
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)

    def test_SAX_FAAgeGroup_F3_Property_43(self):
        MEAN = 4.19341722
        STD = 0.34354021
        PROPERTY_ID = 43
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)

    def test_SAX_FAAgeGroup_F3_Property_44(self):
        MEAN = 0.941523349
        STD = 0.401772326
        PROPERTY_ID = 44
        msg = test_SAX(MEAN, STD, PROPERTY_ID)
        self.assertTrue(msg == "", msg)


if __name__ == '__main__':
    unittest.main()

