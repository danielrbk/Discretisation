from os.path import splitext, exists

import os

from Implementation.ClassicMethods.Expert import Expert
from Implementation.AbstractDiscretisation import Discretization
from Implementation.DataRow import DataRow
from Implementation.Entity import Entity
from typing import Dict, List ,Set
from copy import deepcopy, copy

from Implementation.TD4C.TD4C import TD4C

supported_extensions = [".txt",".csv"]
entities: Dict[int,Entity] = {}


def extract_from_file(file_path, file_extension, class_separator, add_class_information_to_timestamps) -> bool:
    with open(file_path) as f:
        try:
            l = f.readline()
            for line in f:
                dr = DataRow.get_data_from_row(line)
                eid = dr.get_entity_id()
                if eid in entities:
                    e = entities[eid]
                else:
                    e = Entity(eid, class_separator)
                    entities[eid] = e
                e.add_time_stamp(dr.get_temporal_property_id(),dr.get_time_stamp())
            p2e, c2e, p2t = Entity.get_maps()
            # holy loops batman
            if add_class_information_to_timestamps:
                for c in c2e:
                    es = c2e[c]
                    for e in es:
                        ps = e.properties
                        for p in ps:
                            for t in ps[p]:
                                t.ts_class = c
        except:
            return False
    return True


def partition_file_to_properties(file_path):
    folder = file_path.split("\\")[:-1]
    partitions_path = folder + "\\partitions"
    if not exists(partitions_path):
        with open(file_path) as f:
            os.makedirs(partitions_path)
            property_to_file = {}
            for line in f:
                dr = DataRow.get_data_from_row(line)
                pid = dr.get_temporal_property_id()
                if pid not in property_to_file:
                    property_to_file[pid] = open(partitions_path + "\\property%s.csv" % pid)
                property_to_file[pid].write(line)
        for pid in property_to_file:
            property_to_file[pid].close()


def extract_from_file_all_lines(file_path, file_extension, class_separator) -> bool:
    with open(file_path) as f:
        l = f.readline()
        lines = f.readlines()
        drs = [DataRow.get_data_from_row(line) for line in lines]
        entityIds = set([dr.get_entity_id() for dr in drs])
        propertyIds = set([dr.get_temporal_property_id() for dr in drs])
        classes = set([dr.get_time_stamp().value for dr in drs if dr.get_temporal_property_id() == class_separator])
        entities = {eid: Entity(eid,class_separator) for eid in entityIds}
        for dr in drs:
            e = entities[dr.get_entity_id()]
            e.add_time_stamp(dr.get_temporal_property_id(), dr.get_time_stamp())
    return True


def receive_file(file_path, class_separator, class_information):
    file_extension = splitext(file_path)[1]
    if file_extension not in supported_extensions:
        raise Exception("File extension not supported")
    if not extract_from_file(file_path, file_extension, class_separator, class_information):
        raise Exception("File format incorrect")


def discretize_entities(discretizers: List[Discretization]):
    for d in discretizers:
        p2e, c2e, p2t = Entity.get_maps()
        d.discretize(p2e, c2e, p2t)
        write_output(d, c2e, path)


def write_output(discretizer: Discretization, class_to_entities: Dict[int, Set[Entity]], path: str):
    pass


def get_maps_from_file(path, class_seperator, class_information=False):
    #partition_file_to_properties(path)
    receive_file(path, class_seperator, class_information)
    return Entity.get_maps()
    #return None, None, None


if __name__ == "__main__":
    pass



