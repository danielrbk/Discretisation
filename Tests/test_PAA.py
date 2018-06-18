import csv
import unittest
from typing import Dict, List

from os.path import exists

from os import mkdir

from Implementation.AbstractDiscretisation import Discretization
from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.ClassicMethods.Expert import Expert
from Implementation.ClassicMethods.Persist import Persist
from Implementation.Entity import Entity
from Implementation.InputHandler import get_maps_from_file
from Implementation.OutputHandling.Discretization_Out_Handler import write_partition, write_partition_float
from Implementation.TimeInterval import TimeInterval
from Implementation.TD4C.TD4C import TD4C
from Implementation.TimeStamp import TimeStamp
from Tests.Discretization_Result_Generator import get_test_result, assert_almost_equality, compare_time_stamps, \
    compare_time_stamps_p2e, compare_time_stamps_c2e
from Tests.Constants import DATASETS_PATH, STRESS_VALUE_COUNT

DATASET_NAME = "FAAgeGroup_F3"
CLASS_SEPERATOR = -1

DATASET_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + ".csv"
EXPECTED_OUTPUT_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + "_"
PARTITIONS_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\partitions"
ENTITIES_PATH = "%s\\%s\\%s" % (DATASETS_PATH, DATASET_NAME, "entities.csv")
get_maps_from_file(DATASET_PATH, ENTITIES_PATH, CLASS_SEPERATOR)
properties = [1,2,3,4,5,6,39,40,41,42,43,44]
classes = [2,3,4]


class TestMethods(unittest.TestCase):

    def test_PAA_Window_Stress(self):
        cutpoints = []
        TOTAL_POINTS = STRESS_VALUE_COUNT

        message = ""
        for WINDOW_SIZE in range(2,10000):
            p2t = {1: []}
            expected = {1: []}
            for i in range(TOTAL_POINTS + 1,WINDOW_SIZE):
                p2t[1] += [TimeStamp(i+x,i+x,i+x,0) for x in range(WINDOW_SIZE)]
                expected[1].append(TimeStamp(i+(WINDOW_SIZE-1)/2, i, i+WINDOW_SIZE-1, 0))

            d: Discretization = Expert({1:cutpoints},-1, window_size=WINDOW_SIZE)
            d_p2t = d.paa_p2t(p2t)
            t_msg = compare_time_stamps(expected,d_p2t)
            if t_msg != "":
                message += "WINDOW SIZE: %s\n%s\n" % (WINDOW_SIZE,t_msg)
        self.assertTrue(message == "", message)

    def test_PAA_Window_1(self):
        cutpoints = []
        TOTAL_POINTS = 1000
        p2t = {1:[]}
        WINDOW_SIZE = 1

        for i in range(TOTAL_POINTS + 1,WINDOW_SIZE):
            p2t[1].append(TimeStamp(i,i,i,0))

        d: Discretization = Expert({1:cutpoints},-1, window_size=WINDOW_SIZE)
        d_p2t = d.paa_p2t(p2t)
        message = ""
        message += compare_time_stamps(p2t,d_p2t)
        self.assertTrue(message == "", message)

    def test_PAA_Discretization_Difference(self):
        msg = ""
        res = True

        d = EqualWidth(2, 0, window_size=1)
        p2t = {1: []}
        p2t[1] = [TimeStamp(-75, 1, 1, 0),TimeStamp(-25,2,2,0), TimeStamp(1,3,3,0),TimeStamp(25, 4, 4, 0)]  # min = -75, max = 25
        expected_cutpoints = {1: [-25]}
        d.discretize_property({}, {}, p2t, 1)
        real_cutpoints = d.bins_cutpoints
        t_res, t_msg = assert_almost_equality(expected_cutpoints, real_cutpoints)
        msg += t_msg
        res &= t_res

        no_paa_cutpoints = real_cutpoints

        d = EqualWidth(2, 0, window_size=2)
        p2t = {1: []}
        p2t[1] = [TimeStamp(-75, 1, 1, 0), TimeStamp(-25, 2, 2, 0), TimeStamp(1, 3, 3, 0),
                  TimeStamp(25, 4, 4, 0)]  # min = -50 max = 13
        expected_cutpoints = {1: [-50 + 63/2]}
        d.discretize_property({}, {}, p2t, 1)
        real_cutpoints = d.bins_cutpoints
        t_res, t_msg = assert_almost_equality(expected_cutpoints, real_cutpoints)
        if t_msg != "":
            t_msg = "\n" + t_msg
        msg += t_msg
        res &= t_res

        paa_cutpoints = real_cutpoints

        t_res, t_msg = assert_almost_equality({1:no_paa_cutpoints},{1:paa_cutpoints})
        if t_res:
            msg += "\nExpected different cutpoints with PAA! Got %s" % no_paa_cutpoints
            res = False

        self.assertTrue(res, msg)

if __name__ == '__main__':
    unittest.main()

