import csv
from typing import Dict, List, Set, Tuple

from Implementation.AbstractDiscretisation import Discretization
from Implementation.Entity import Entity
from Implementation.InputHandler import get_maps_from_file
from Implementation.TimeStamp import TimeStamp


def get_test_result(output_path: str, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]], property_to_timestamps: Dict[int, List[TimeStamp]], discretization: Discretization) -> Tuple:
    expected_dict = {}
    expected = get_expected_output(output_path, expected_dict)
    discretization.discretize(property_to_entities, class_to_entities,property_to_timestamps)
    real = discretization.bins_cutpoints
    return real, expected


def get_expected_output(path, property_to_cutpoints: Dict[int, List]):
    with open(path, 'r') as f:
        o = csv.reader(f)
        for line in o:
            break
        for line in o:
            p = line[1]
            fr = line[-2]
            if p in property_to_cutpoints:
                property_to_cutpoints[p].append(fr)
            else:
                property_to_cutpoints[p] = []
    return property_to_cutpoints


def print_maps(property_to_entities, class_to_entities, property_to_timestamps):
    for c in class_to_entities:
        print(c)
        for e in class_to_entities[c]:
            print(e.__str__())