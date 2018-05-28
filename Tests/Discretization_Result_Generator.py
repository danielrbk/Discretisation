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


def assert_almost_equality(d1: Dict[int, List[float]], d2: Dict[int, List[float]]):
    if d1.keys() != d2.keys():
        return False, "Keys are different\nReal keys: %s\nExpected keys: %s" % (d1.keys(),d2.keys())
    for key in d1.keys():
        d1a = np.array(d1[key])
        d2a = np.array(d2[key])
        try:
            eq = np.testing.assert_almost_equal(d1a,d2a)
        except:
            return False, "Not equal for property: %s\nReal: %s\nExpected: %s" % (key, d1a, d2a)

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

