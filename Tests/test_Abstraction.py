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
from Tests.Constants import DATASETS_PATH

DATASET_NAME = "FAAgeGroup_F3"
CLASS_SEPERATOR = -1

DATASET_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + ".csv"
EXPECTED_OUTPUT_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + "_"
PARTITIONS_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\partitions"
ENTITIES_PATH = "%s\\%s\\%s" % (DATASETS_PATH, DATASET_NAME, "entities.csv")
get_maps_from_file(DATASET_PATH, ENTITIES_PATH, CLASS_SEPERATOR)
properties = [1,2,3,4,5,6,39,40,41,42,43,44]
classes = [2,3,4]


def check_file_similiarity(lines, msg, out_folder, p):
    for c in classes:
        with open(out_folder + "\\property%s_class%s.temp" % (p, c)) as f:
            lines += [line.rstrip().split(',') for line in f.readlines()]
    lines = [(int(x[-1]), int(x[0]), float(x[-2])) for x in lines]
    lines = list(sorted(lines))
    expected_lines_res = []
    with open(PARTITIONS_PATH + "\\property%s.csv" % p) as f:
        expected_lines = [line.rstrip().split(',') for line in f.readlines()]
        for line in expected_lines:
            expected_lines_res.append((int(line[0]), int(line[2]), float(line[3])))
    if lines != expected_lines_res:
        lines = set(lines)
        s = lines.symmetric_difference(expected_lines_res)
        msg += "PROPERTY %s -- Difference between lines:\n%s\n" % (p, s)
    return msg

class TestMethods(unittest.TestCase):

    def test_Abstraction_Most_Bins(self):
        cutpoints = []
        TOTAL_POINTS = 1000
        p2t = {1:[]}
        expected = {1:[]}
        c2e = {}
        p2e = {}
        for i in range(1,TOTAL_POINTS + 1):
            p2t[1].append(TimeStamp(i,i,i,i))
            expected[1].append(TimeStamp(i-1,i,i,i))
            cutpoints.append(i+0.5)
        d: Discretization = Expert({1:cutpoints},-1)
        d_p2e, d_c2e, d_p2t = d.discretize_property(p2e, c2e, p2t,1)
        message = ""
        message += compare_time_stamps(expected,d_p2t)
        self.assertTrue(message == "", message)

    def test_Abstraction_MaxGap_0_Bins_2(self):
        cutpoints = []
        TOTAL_POINTS = 1000
        p2t = {1: []}
        c2e = {}
        p2e = {}
        for i in range(1, TOTAL_POINTS + 1):
            p2t[1].append(TimeStamp(i, i, i, 0))
        cutpoints = [500]
        d: Discretization = Expert({1: cutpoints}, 0)
        d_p2e, d_c2e, d_p2t = d.discretize_property(p2e, c2e, p2t, 1)
        expected = {1: []}
        lst = expected[1]
        lst.append(TimeStamp(0,1,499,0))
        lst.append(TimeStamp(1, 500, 1000, 0))
        message = ""
        message += compare_time_stamps(expected, d_p2t)
        self.assertTrue(message == "", message)

    def test_Abstraction_MaxGap_0_Bins_3(self):
        cutpoints = []
        TOTAL_POINTS = 1000
        p2t = {1: []}
        c2e = {}
        p2e = {}
        for i in range(1, TOTAL_POINTS + 1):
            p2t[1].append(TimeStamp(i, i, i, 0))
        cutpoints = [333,666]
        d: Discretization = Expert({1: cutpoints}, 0)
        d_p2e, d_c2e, d_p2t = d.discretize_property(p2e, c2e, p2t, 1)
        expected = {1: []}
        lst = expected[1]
        lst.append(TimeStamp(0, 1, 332, 0))
        lst.append(TimeStamp(1, 333, 665, 0))
        lst.append(TimeStamp(2, 666, 1000, 0))
        message = ""
        message += compare_time_stamps(expected, d_p2t)
        self.assertTrue(message == "", message)

    def test_Abstraction_MaxGap_0_Bins_2_Different_Entities(self):
        cutpoints = []
        TOTAL_POINTS = 1000
        p2t = {1: []}
        expected = {1: []}
        c2e = {}
        p2e = {}
        cutpoints = [500]
        for i in range(1, TOTAL_POINTS + 1):
            expected_bin = 0
            if i>=500:
                expected_bin = 1
            if i%2 == 0:
                p2t[1].append(TimeStamp(i, i, i, 0))
                expected[1].append(TimeStamp(expected_bin, i, i, 0))
            else:
                p2t[1].append(TimeStamp(i, i, i, 1))
                expected[1].append(TimeStamp(expected_bin, i, i, 1))
        d: Discretization = Expert({1: cutpoints}, 0)
        d_p2e, d_c2e, d_p2t = d.discretize_property(p2e, c2e, p2t, 1)
        message = ""
        message += compare_time_stamps(expected, d_p2t)
        self.assertTrue(message == "", message)

    def test_Abstraction_MaxGap_1_Bins_2_Different_Entities(self):
        cutpoints = []
        TOTAL_POINTS = 1000
        p2t = {1: []}
        expected = {1: []}
        c2e = {}
        p2e = {}
        cutpoints = [500]
        for i in range(1, TOTAL_POINTS + 1):
            if i % 2 == 0:
                p2t[1].append(TimeStamp(i, i, i, 0))
            else:
                p2t[1].append(TimeStamp(i, i, i, 1))

        expected[1].append(TimeStamp(0, 1, 499, 1))
        expected[1].append(TimeStamp(0, 2, 498, 0))
        expected[1].append(TimeStamp(1, 500, 1000, 0))
        expected[1].append(TimeStamp(1, 501, 999, 1))
        d: Discretization = Expert({1: cutpoints}, 1)
        d_p2e, d_c2e, d_p2t = d.discretize_property(p2e, c2e, p2t, 1)
        message = ""
        message += compare_time_stamps(expected, d_p2t)
        self.assertTrue(message == "", message)

    def test_Abstraction_Ignore_Properties(self):
        cutpoints = []
        TOTAL_POINTS = 1000
        p2t = {1: [],2: []}
        c2e = {}
        p2e = {}
        for i in range(1, TOTAL_POINTS + 1):
            p2t[1].append(TimeStamp(i, i, i, i))
        cutpoints.append(5)
        p2t[2].append(TimeStamp(0,0,0,0))
        expected = {1: p2t[1], 2: [TimeStamp(0,0,0,0)]}
        d: Discretization = Expert({2: cutpoints}, -1)
        d_p2e, d_c2e, d_p2t = d.discretize_property(p2e, c2e, p2t, 2)
        message = ""
        message += compare_time_stamps(p2t, d_p2t)
        self.assertTrue(message == "", message)

    def test_Abstraction_No_Impact_p2t(self):
        p2t = {1: [TimeStamp(0,1,1,0,0), TimeStamp(0,1,1,1,0), TimeStamp(1,1,1,2,1), TimeStamp(1,1,1,3,1)]}
        d: Discretization = Expert({1:[1.5]}, 0)
        d_p2e, d_c2e, d_p2t = d.discretize_property({},{}, p2t, 1)
        message = ""
        message += compare_time_stamps(p2t, d_p2t)
        self.assertTrue(message != "", "Original data was changed during abstraction")

    def test_Abstraction_No_Impact_p2e(self):
        e0: Entity = Entity(0,0,-1)
        e1: Entity = Entity(1,0,-1)
        e2: Entity = Entity(2,1,-1)
        e3: Entity = Entity(3,1,-1)
        e0.properties = {1: [TimeStamp(0,1,1,0,0)]}
        e1.properties = {1: [TimeStamp(0,1,1,1,0)]}
        e2.properties = {1: [TimeStamp(1,1,1,2,1)]}
        e3.properties = {1: [TimeStamp(1,1,1,3,1)]}
        p2e = {1: {e0, e1, e2, e3}}
        d: Discretization = Expert({1:[1.5]}, 0)
        d_p2e, d_c2e, d_p2t = d.discretize_property(p2e, {}, {}, 1)
        message = ""
        message += compare_time_stamps_p2e(p2e, d_p2e)
        self.assertTrue(message != "", "Original data was changed during abstraction")

    def test_Abstraction_No_Impact_c2e(self):
        e0: Entity = Entity(0,0,-1)
        e1: Entity = Entity(1,0,-1)
        e2: Entity = Entity(2,1,-1)
        e3: Entity = Entity(3,1,-1)
        e0.properties = {1: [TimeStamp(0,1,1,0,0)]}
        e1.properties = {1: [TimeStamp(0,1,1,1,0)]}
        e2.properties = {1: [TimeStamp(1,1,1,2,1)]}
        e3.properties = {1: [TimeStamp(1,1,1,3,1)]}
        c2e = {0: {e0,e1}, 1: {e2,e3}}
        d: Discretization = Expert({1:[1.5]}, 0)
        d_p2e, d_c2e, d_p2t = d.discretize_property({}, c2e, {}, 1)
        message = ""
        message += compare_time_stamps_c2e(c2e, d_c2e)
        self.assertTrue(message != "", "Original data was changed during abstraction")

    def test_write_output_p2t_no_information_loss(self):
        out_folder = "test_files_folder"
        if not exists(out_folder):
            mkdir(out_folder)
        msg = ""
        for p in properties:
            m = {}
            d = EqualWidth(3,0)
            d.property_folder = PARTITIONS_PATH
            d.load_property_to_timestamps(m,p)
            write_partition_float({},{},m,out_folder,p)
            lines = []
            msg = check_file_similiarity(lines, msg, out_folder, p)
        self.assertTrue(msg == "", msg)

    def test_write_output_p2e_no_information_loss(self):
        out_folder = "test_files_folder"
        if not exists(out_folder):
            mkdir(out_folder)
        msg = ""
        for p in properties:
            m = {}
            d = EqualWidth(3,0)
            d.property_folder = PARTITIONS_PATH
            d.load_property_to_entity(m,p)
            write_partition_float(m,{},{},out_folder,p)
            lines = []
            msg = check_file_similiarity(lines, msg, out_folder, p)
        self.assertTrue(msg == "", msg)

    def test_write_output_c2e_no_information_loss(self):
        out_folder = "test_files_folder"
        if not exists(out_folder):
            mkdir(out_folder)
        msg = ""
        for p in properties:
            m = {}
            d = EqualWidth(3,0)
            d.property_folder = PARTITIONS_PATH
            d.load_class_to_entity(m,p)
            write_partition_float({},m,{},out_folder,p)
            lines = []
            msg = check_file_similiarity(lines, msg, out_folder, p)
        self.assertTrue(msg == "", msg)




if __name__ == '__main__':
    unittest.main()

