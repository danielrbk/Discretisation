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


class TestMethods(unittest.TestCase):

    def test_synthetic_EQF_2(self):
        d = EqualFrequency(2, 0)
        p2t = {1:[]}
        p2t[1] = [TimeStamp(-75,1,1,0),TimeStamp(25,1,1,0)] # min = -75, max = 25
        expected_cutpoints = {1:[-25]}
        d.discretize_property_without_abstracting({},{},p2t,1)
        real_cutpoints = d.bins_cutpoints
        res, msg = assert_almost_equality(expected_cutpoints,real_cutpoints)
        self.assertTrue(res,msg)



if __name__ == '__main__':
    unittest.main()

