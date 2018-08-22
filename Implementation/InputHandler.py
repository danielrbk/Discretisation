import csv
from math import floor
from os.path import splitext, exists

import os

from Implementation.ClassicMethods.Expert import Expert
from Implementation.AbstractDiscretisation import Discretization
from Implementation.Constants import CLASS_SEPARATOR, DEBUG_MODE
from Implementation.DataRow import DataRow
from Implementation.Entity import Entity
from typing import Dict, List ,Set
from copy import deepcopy, copy

from Implementation.TD4C.TD4C import TD4C
from dateutil import parser

supported_extensions = [".txt",".csv"]
entities: Dict[int,Entity] = {}


def extract_from_file(file_path, file_extension, class_separator, add_class_information_to_timestamps) -> bool:
    with open(file_path) as f:
        try:
            line_number = 0
            l = f.readline()
            for line in f:
                dr = DataRow.get_data_from_row(line)
                eid = dr.get_entity_id()
                if eid in entities:
                    e = entities[eid]
                else:
                    e = Entity(eid, 0, class_separator)
                    entities[eid] = e
                e.add_time_stamp(dr.get_temporal_property_id(),dr.get_time_stamp())
                line_number += 1
                if line_number % 100000 == 0:
                    print("%s/%s" %(line_number//100000,97000000//100000))
            p2e, c2e, p2t = Entity.get_maps()
            # holy loops batman
            if add_class_information_to_timestamps:
                for c in c2e:
                    es = c2e[c]
                    for e in es:
                        ps = e.properties
                        e.entity_class = c
                        for p in ps:
                            for t in ps[p]:
                                t.ts_class = c
        except:
            return False
    return True

"""
def format_timestamps_to_int(file_path,entities_path):
    with open(file_path) as f, open(file_path + "t", 'w') as w:
        max_time = 
        for line in f:
            time = line.rstrip().split(',')[2]
"""


def format_timestamps_to_int(file_path, entities_path):
    pass


def partition_file_to_properties(file_path,entities_path):
    folder = file_path.split("\\")[:-1]
    partitions_path = "\\".join(folder) + "\\partitions"
    property_to_file = {}
    class_to_entity_count = {}
    line_count = 0
    if DEBUG_MODE or not exists(partitions_path):
        print("No partitions found, creating partitions...")
        e_file = None
        if not exists(entities_path):
            e_file = open(entities_path, 'w', newline='')
        with open(file_path) as f:
            entities = set()
            if not exists(partitions_path):
                os.makedirs(partitions_path)
            f.readline()
            for line in f:
                if line_count%1000000 == 0:
                    print("Wrote %s lines..." % line_count)
                line_count += 1
                if line_count == 1:
                    try:
                        time = int(line.rstrip().split(',')[2])
                    except:
                        format_timestamps_to_int(file_path, entities_path)
                        return            
                dr = DataRow.get_data_from_row(line)
                if dr.entity_id not in entities:
                    entities.add(dr.entity_id)
                pid = dr.get_temporal_property_id()
                if pid == CLASS_SEPARATOR:
                    c = floor(dr.get_time_stamp().value)
                    if c in class_to_entity_count:
                        class_to_entity_count[c] += 1
                    else:
                        class_to_entity_count[c] = 1
                if pid not in property_to_file:
                    property_to_file[pid] = open(partitions_path + "\\property%s.csv" % pid, 'w')
                property_to_file[pid].write(line)
            if e_file is not None:
                entity_csv = csv.writer(e_file)
                entity_csv.writerow(["id","name"])
                for e in entities:
                    entity_csv.writerow([str(e),"Entity%s" % e])
                e_file.close()
        for pid in property_to_file:
            property_to_file[pid].close()
        with open(partitions_path + "\\properties.csv", 'w', newline='') as f, open(partitions_path + "\\class_to_entity_count.csv", 'w', newline='') as c:
            input = csv.writer(f)
            class_input = csv.writer(c)
            lst = list(property_to_file.keys())
            if CLASS_SEPARATOR in lst:
                lst.remove(CLASS_SEPARATOR)
            input.writerow(lst)
            classed_entities = 0
            for c in class_to_entity_count:
                classed_entities += class_to_entity_count[c]
                class_input.writerow([c,class_to_entity_count[c]])
            non_classed_entities = len(entities) - classed_entities
            if non_classed_entities != 0:
                class_input.writerow([-10000,non_classed_entities])
    else:
        print("Partitions found. Continuing...")


def receive_file(file_path, class_separator, class_information):
    file_extension = splitext(file_path)[1]
    if file_extension not in supported_extensions:
        raise Exception("File extension not supported")
    if not extract_from_file(file_path, file_extension, class_separator, class_information):
        raise Exception("File format incorrect")


def get_maps_from_file(path, entities_path, class_seperator, class_information=False):
    return partition_file_to_properties(path, entities_path)
    #receive_file(path, class_seperator, class_information)
    #return Entity.get_maps()
    #return None, None, None


if __name__ == "__main__":
    pass



