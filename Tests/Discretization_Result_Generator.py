import csv
from typing import Dict, List, Set, Tuple

from Implementation.AbstractDiscretisation import Discretization
from Implementation.Entity import Entity
from Implementation.InputHandler import get_maps_from_file
from Implementation.TimeStamp import TimeStamp
import numpy as np

def get_test_result(output_path: str, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]], property_to_timestamps: Dict[int, List[TimeStamp]], discretization: Discretization) -> Tuple:
    expected_dict = {}
    properties_file = "\\".join(output_path.split("\\")[:-1]) + "\\partitions\\properties.csv"
    with open(properties_file) as f:
        in_f = csv.reader(f)
        for line in in_f:
            property_ids = [int(x) for x in list(line)]
    expected = get_expected_output(output_path, expected_dict)
    for property_id in property_ids:
        property_to_entities = {}
        class_to_entities = {}
        property_to_timestamps = {}
        discretization.discretize_property_without_abstracting(property_to_entities, class_to_entities,property_to_timestamps,property_id)
    real = discretization.bins_cutpoints
    return real, expected


def compare_time_stamps(expected,result):
    message = ""
    if sorted(expected.keys()) != sorted(result.keys()):
        message += "Property to timestamps keys inequal. Expected: %s, Got: %s" % (expected.keys(), result.keys())
    for key in expected.keys():
        message += compare_time_stamps_helper(expected,result,key)
    return message


def compare_time_stamps_helper(expected,result,property_id):
    message = ""
    res = result[property_id]
    TOTAL_POINTS = len(expected[property_id])
    if TOTAL_POINTS < len(res):
        message += "Result is bigger than expected\n"
    else:
        if TOTAL_POINTS > len(res):
            message += "Result is smaller than expected\n"

        for i in range(len(res)):
            expected_ts = expected[property_id][i]
            res_ts = res[i]
            if expected_ts.value != res_ts.value:
                message += "TIMESTAMP VALUE: Index %s -- Expected: %s. Got: %s.\n" % (i, expected_ts.value, res_ts.value)
            elif expected_ts.start_point != res_ts.start_point:
                message += "TIMESTAMP START POINT: Index %s -- Expected: %s. Got: %s.\n" % (
                    i, expected_ts.start_point, res_ts.start_point)
            elif expected_ts.end_point != res_ts.end_point:
                message += "TIMESTAMP END POINT: Index %s -- Expected: %s. Got: %s.\n" % (
                    i, expected_ts.end_point, res_ts.end_point)
            elif expected_ts.end_point != res_ts.end_point:
                message += "TIMESTAMP END POINT: Index %s -- Expected: %s. Got: %s.\n" % (
                    i, expected_ts.end_point, res_ts.end_point)
    return message


def compare_time_stamps_p2e(expected, result):
    message = ""
    if sorted(expected.keys()) != sorted(result.keys()):
        message += "Property to entities keys inequal. Expected: %s, Got: %s" % (expected.keys(), result.keys())
    for key in expected.keys():
        message += compare_time_stamps_p2e_helper(expected,result,key)
    return message


def compare_time_stamps_p2e_helper(expected,result, property_id):
    message = ""
    res = result[property_id]

    TOTAL_POINTS = len(expected[property_id])
    if TOTAL_POINTS < len(res):
        message += "Result is bigger than expected\n"
    else:
        if TOTAL_POINTS > len(res):
            message += "Result is smaller than expected\n"
        expected_entities = sorted(expected[property_id],key=lambda e:e.get_entity_id())
        real_entities = sorted(result[property_id],key=lambda e:e.get_entity_id())
        expected_ids = [e.get_entity_id() for e in expected_entities]
        real_ids = [e.get_entity_id() for e in real_entities]
        if expected_ids != real_ids:
            message += "Entities for property id %s different -- Expected: %s, Got: %s\n" % (property_id,expected_ids,real_ids)
        else:
            res = ""
            for expected_e, real_e in zip(expected_entities,real_entities):
                res = compare_time_stamps(expected_e.properties, real_e.properties)
                if res != "":
                    message += "Timestamps different for entity %s, Error Log:\n" % (expected_e.get_entity_id())
                    message += res
                res = ""
    return message


def compare_time_stamps_c2e(expected,result):
    message = ""
    if list(sorted(expected.keys())) != list(sorted(result.keys())):
        message += "Different classes between maps"
    else:
        res = ""
        for expected_c, real_c in zip(expected.keys(), result.keys()):
            res = compare_time_stamps_p2e({1: expected[expected_c]}, {1: result[real_c]})
            if res != "":
                message += "Timestamps different for class %s, Error Log:\n" % (expected_c)
                message += res
            res =""
    return message


def assert_almost_equality(d1: Dict[int, List[float]], d2: Dict[int, List[float]]):
    if d1.keys() != d2.keys():
        return False, "Keys are different\nGot keys: %s\nExpected keys: %s" % (d1.keys(),d2.keys())
    message = ""
    for key in d1.keys():
        d1a = np.array(d1[key])
        d2a = np.array(d2[key])
        try:
            eq = np.testing.assert_almost_equal(d1a,d2a)
        except:
            message += "Not equal for property: %s\nGot: %s\nExpected: %s\n" % (key, d1a, d2a)
    if message != "":
        return False, message
    return True, ""

def get_expected_output(path, property_to_cutpoints: Dict[int, List]):
    with open(path, 'r') as f:
        o = csv.reader(f)
        for line in o:
            break
        for line in o:
            p = int(line[1])
            fr = float(line[-2])
            if p in property_to_cutpoints:
                property_to_cutpoints[p].append(fr)
            else:
                property_to_cutpoints[p] = []
    return property_to_cutpoints


def print_maps(property_to_entities, class_to_entities, property_to_timestamps):
    for c in class_to_entities:
        print("")
        print("------")
        print("Class ",c)
        for e in class_to_entities[c]:
            print(e.__str__())
        print("------")

