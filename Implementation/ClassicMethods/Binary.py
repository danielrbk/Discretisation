import math

from Implementation.AbstractDiscretisation import Discretization
from typing import Dict, List, Set

from Implementation.BinInterval import BinInterval
from Implementation.Entity import Entity
from Implementation.TimeInterval import TimeInterval
from Implementation.TimeStamp import TimeStamp
import numpy as np


def __count_class__(class_val, property_class_list):
    """

    :param class_val: the class to count
    :param property_class_list:  a list of (property_value, class)
    :return: The number of occurrences of class_val in property_class_list
    """
    count = 0
    for item in property_class_list:
        if item[1] == class_val:
            count += 1
    return count


def entropy(property_class_list, class_list):
    """

    :param property_class_list:  a list of (property_value, class)
    :param class_list: possible classes to consider
    :return: calculated entropy according the paper
    """
    ent_res = 0
    for i, val in enumerate(class_list):
        class_proportion = __count_class__(val, property_class_list)
        class_proportion = class_proportion / len(property_class_list)
        if class_proportion != 0:
            ent_res += (class_proportion * math.log(class_proportion, 10))

    ent_res = - ent_res
    return ent_res


def class_information_entropy(subset_1, subset_2, classes_list):
    s1_size = len(subset_1)
    s2_size = len(subset_2)
    total_set_size = s1_size + s2_size
    res = ((s1_size / total_set_size) * entropy(subset_1, classes_list)) + \
          ((s2_size / total_set_size) * entropy(subset_2, classes_list))
    return -res


class Binary(Discretization):
    def get_map_used(self):
        return "property_to_entities"

    def set_bin_ranges(self, property_to_entities: Dict[int, Set[Entity]], class_to_entities: Dict[int, Set[Entity]],
                       property_to_timestamps: Dict[int, List[TimeStamp]]):
        cutpoints = self.parallel_cutpoint_set(property_to_entities, class_to_entities, property_to_timestamps)
        return cutpoints

    def set_bin_ranges_for_property(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]], property_id: int):
        if not property_to_entities:
            self.load_property_to_entity(property_to_entities, property_id)
        matching_entities = property_to_entities[property_id]
        matching_classes = set()
        property_value_class_list = []
        c_value = None
        for e in matching_entities:
            p_value = e.properties[property_id][0].value
            for _class in class_to_entities:
                for _e in class_to_entities[_class]:
                    if _e.entity_id == e.entity_id:
                        c_value = _class
                        break
                if c_value is not None:
                    break

            #c_value = e.class_separator
            matching_classes.add(c_value)
            property_value_class_list.append((p_value, c_value))

        # Now we have the mapping between property values and the corresponding classes
        # Sort by property value
        property_value_class_list = sorted(property_value_class_list, key=lambda tup: tup[0])
        property_values_count = len(property_value_class_list)
        print(property_value_class_list)
        candidate_cut_points_calc = np.zeros(property_values_count, dtype=float)

        for partition_index, val in enumerate(property_value_class_list):
            if partition_index != 0:

            # if partition_index == len(property_value_class_list) - 1:
            #     break
                subset_1 = property_value_class_list[:partition_index]
                subset_2 = property_value_class_list[partition_index:]

                candidate_cut_points_calc[partition_index] = class_information_entropy(subset_1, subset_2,
                                                                                       matching_classes)

        cut_point_index = candidate_cut_points_calc.argmin()
        print(candidate_cut_points_calc)
        return [property_value_class_list[cut_point_index][0]]

    def write_auxiliary_information(self, property_to_entities: Dict[int, Set[Entity]],
                                    class_to_entities: Dict[int, Set[Entity]],
                                    property_to_timestamps: Dict[int, List[TimeStamp]],
                                    path: str):
        pass

    def get_discretization_name(self):
        return "BINARY_%s" % self.bin_count

    def __init__(self, bin_count, max_gap):
        super(Binary, self).__init__(max_gap)
        self.bin_count = int(bin_count)

#
if __name__ == '__main__':
    print(math.log(0.5,10)*0.5)
    print([1,2,3][:1])
    p_to_ent = {}
    e1 = Entity(1, 1)
    e2 = Entity(2, 1)
    e3 = Entity(3, 2)
    e1.properties[0] = [TimeStamp(10, TimeInterval(0, 1))]
    e2.properties[0] = [TimeStamp(15, TimeInterval(2, 3))]
    e3.properties[0] = [TimeStamp(7, TimeInterval(4, 5))]
    binary = Binary(2)
    p_to_ent[0] = set()
    p_to_ent[0].add(e1)
    p_to_ent[0].add(e2)
    p_to_ent[0].add(e3)
    c_to_ent = {1: set(), 2: set()}
    c_to_ent[1].add(e1)
    c_to_ent[1].add(e2)
    c_to_ent[2].add(e3)

    print(binary.set_bin_ranges_for_property(p_to_ent, c_to_ent, {}, 0))
    # x = set()
    # y = set()
    # a = [8, 2, 3, 4, 5, 6]
    # a_arr = np.array(a)
    # print(a_arr.argmin())
    # print(a[0:])

