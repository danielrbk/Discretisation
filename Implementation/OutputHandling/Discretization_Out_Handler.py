import bisect
import csv
import os
from math import floor, log
from typing import Dict, Set, List

from Implementation.Constants import EXTREME_VAL
from Implementation.TimeStamp import TimeStamp
from Implementation.AbstractDiscretisation import Discretization
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.Entity import Entity
from Implementation.InputHandler import get_maps_from_file


def write_partition(p2e: Dict[int, Set[Entity]], c2e: Dict[int, Set[Entity]], p2t: Dict[int, List[TimeStamp]],out_folder, property_id):
    open_file = None
    start = True
    if p2t:
        sorted_by_entity_start: List[TimeStamp] = sorted(p2t[property_id],key=lambda x: (x.ts_class,x.entity_id, x.start_point, x.end_point))
        e_id = c_id = float('-inf')
        for ts in sorted_by_entity_start:
            if ts.ts_class != c_id:
                start = True
                if open_file is not None:
                    open_file.close()
                c_id = ts.ts_class
                open_file = open(out_folder + "\\property%s_class%s.temp" % (property_id,c_id), 'w')
            open_file.write("%s,%s,%s,%s\n" % (ts.start_point, ts.end_point, floor(ts.value), ts.entity_id))
    elif p2e:
        entities = sorted(p2e[property_id],key=lambda x:(x.entity_class,x.entity_id))
        c_id = float('-inf')
        for e in entities:
            if e.entity_class != c_id:
                start = True
                if open_file is not None:
                    open_file.close()
                c_id = e.entity_class
                open_file = open(out_folder + "\\property%s_class%s.temp" % (property_id,c_id), 'w')
            for ts in e.properties[property_id]:
                open_file.write("%s,%s,%s,%s\n" % (ts.start_point, ts.end_point, floor(ts.value), e.entity_id))
    else:
        for c_id in c2e:
            with open(out_folder + "\\property%s_class%s.temp" % (property_id,c_id), 'w') as f:
                for e in sorted(c2e[c_id], key=lambda x:x.entity_id):
                    for ts in e.properties[property_id]:
                        f.write("%s,%s,%s,%s\n" % (ts.start_point, ts.end_point, floor(ts.value), e.entity_id))

def write_partition_float(p2e: Dict[int, Set[Entity]], c2e: Dict[int, Set[Entity]], p2t: Dict[int, List[TimeStamp]],out_folder, property_id):
    open_file = None
    start = True
    if p2t:
        sorted_by_entity_start: List[TimeStamp] = sorted(p2t[property_id],key=lambda x: (x.ts_class,x.entity_id, x.start_point, x.end_point))
        e_id = c_id = float('-inf')
        for ts in sorted_by_entity_start:
            if ts.ts_class != c_id:
                start = True
                if open_file is not None:
                    open_file.close()
                c_id = ts.ts_class
                open_file = open(out_folder + "\\property%s_class%s.temp" % (property_id,c_id), 'w')
            open_file.write("%s,%s,%s,%s\n" % (ts.start_point, ts.end_point, float(ts.value), ts.entity_id))
    elif p2e:
        entities = sorted(p2e[property_id],key=lambda x:(x.entity_class,x.entity_id))
        c_id = float('-inf')
        for e in entities:
            if e.entity_class != c_id:
                start = True
                if open_file is not None:
                    open_file.close()
                c_id = e.entity_class
                open_file = open(out_folder + "\\property%s_class%s.temp" % (property_id,c_id), 'w')
            for ts in e.properties[property_id]:
                open_file.write("%s,%s,%s,%s\n" % (ts.start_point, ts.end_point, float(ts.value), e.entity_id))
    else:
        for c_id in c2e:
            with open(out_folder + "\\property%s_class%s.temp" % (property_id,c_id), 'w') as f:
                for e in sorted(c2e[c_id], key=lambda x:x.entity_id):
                    for ts in e.properties[property_id]:
                        f.write("%s,%s,%s,%s\n" % (ts.start_point, ts.end_point, float(ts.value), e.entity_id))

def merge_partitions(out_folder, vmap_path, method_name,properties_list, class_list, class_to_entity_count, bins_cutpoints, entity_count):
    folder_path = out_folder
    states_path = folder_path + "\\" + "states.csv"
    finished_path = folder_path + "\\" + "finished.log"
    entities_path = folder_path + "\\" + "entities_class_"
    property_to_base = {}
    class_to_sid_to_count = {}
    last_base = 0
    property_to_state_to_count = {}
    sid_to_count = {}
    cutpoints = bins_cutpoints
    for key in sorted(cutpoints.keys()):
        property_to_base[key] = last_base
        last_base += len(cutpoints[key]) + 1

    if len(class_list) == 0:
        class_list.append("None")
        class_to_entity_count["None"] = entity_count
    for c in class_list:
        e_id = float('-inf')
        with open(out_folder + "\\" + method_name + '_Class' + str(c) + '.txt', 'w') as f,\
                open(out_folder + "\\karmalegov_Class" + str(c) + ".csv", 'w') as k_f:
            f.write('startToncepts\n')
            k_f.write('startToncepts\n')
            f.write('numberOfEntities,' + str(class_to_entity_count[c]))
            k_f.write('numberOfEntities,' + str(class_to_entity_count[c]))
            property_to_file = {p: open(out_folder + "\\property%s_class%s.temp" % (p,c)) for p in properties_list}
            property_to_line = {p: property_to_file[p].readline().rstrip().split(",") for p in properties_list}
            lines = [(int(property_to_line[p][-1]),int(property_to_line[p][0]),int(property_to_line[p][1]),int(property_to_line[p][2]),p) for p in property_to_line]
            lines = sorted(lines)
            while len(lines) != 0:
                new_eid = lines[0][0]
                if new_eid != e_id:
                    f.write("\n%s;\n" % new_eid)
                    k_f.write("\n%s;\n" % new_eid)
                    e_id = new_eid
                else:
                    f.write(";")
                    k_f.write(";")
                p = int(lines[0][4])
                if p in property_to_state_to_count:
                    sid_to_count = property_to_state_to_count[p]
                else:
                    property_to_state_to_count[p] = {}
                    sid_to_count = property_to_state_to_count[p]
                bin = int(lines[0][3])
                state_id = property_to_base[p] + bin
                if bin in sid_to_count:
                    sid_to_count[bin] += 1
                else:
                    sid_to_count[bin] = 1
                f.write("%s,%s,%s,%s" % (lines[0][1],lines[0][2],lines[0][3],p))
                k_f.write("%s,%s,%s,%s" % (lines[0][1],lines[0][2],state_id,p))
                property_to_line[p] = property_to_file[p].readline().rstrip()
                lines.pop(0)
                if not property_to_line[p]:
                    property_to_file[p].close()
                    os.remove(property_to_file[p].name)
                else:
                    line = property_to_line[p].split(",")
                    line = (int(line[-1]),int(line[0]),int((line[1])),int(line[2]),p)
                    bisect.insort(lines,line)

    write_auxiliary_output(vmap_path,states_path,properties_list,bins_cutpoints,method_name, property_to_state_to_count)
    with open(finished_path, 'w') as f:
        f.write("done")


def write_auxiliary_output(vmap_path,states_path,properties_list,cutpoints, method_name, property_to_state_to_count):
    id_to_name = {}
    property_to_state_to_entropy = calculate_property_entropy(property_to_state_to_count)
    try:
        with open(vmap_path) as in_file:
            input = csv.reader(in_file)
            for line in input:
                id = line[0]
                name = line[1]
                if name == "TemporalPropertyName":
                    continue
                else:
                    id_to_name[int(id)] = name
    except FileNotFoundError:
        for property_id in properties_list:
            id_to_name[int(property_id)] = "Property_%s" % (property_id)

    with open(states_path, 'w', newline='') as out_file:
        out = csv.writer(out_file)
        out.writerow(
            ["StateID", "IntervalClusterID", "TemporalPropertyID", "TemporalPropertyName", "MethodName", "Error1",
             "Entropy", "BinID", "BinLabel", "BinFrom", "BinTo", "IntervalClusterLabel", "IntervalClusterCentroid",
             "IntervalClusterVariance", "IntervalClusterSize"])
        state_id = 0
        for key in sorted(cutpoints.keys()):
            bin_id = 0
            state_to_entropy = property_to_state_to_entropy[key]
            from_val = -EXTREME_VAL
            for cutpoint in cutpoints[key]:
                entropy = ""
                if bin_id in state_to_entropy:
                    entropy = state_to_entropy[bin_id]
                else:
                    entropy = "undefined"
                out.writerow(
                    [str(state_id), "1", str(key), id_to_name[key], method_name, "0", entropy, bin_id, "Level%s" % bin_id,
                     from_val, cutpoint, "NoClustering", "1", "0", "0"])
                from_val = cutpoint
                state_id += 1
                bin_id += 1
            entropy = ""
            if bin_id in state_to_entropy:
                entropy = state_to_entropy[bin_id]
            else:
                entropy = "undefined"
            out.writerow(
                [str(state_id), "1", str(key), id_to_name[key], method_name, "0",  entropy, bin_id, "Level%s" % bin_id,
                 from_val, EXTREME_VAL, "NoClustering", "1", "0", "0"])
            state_id += 1
            bin_id += 1


def calculate_property_entropy(property_to_state_to_count):
    property_to_state_to_entropy = {}
    for property_id in property_to_state_to_count:
        property_to_state_to_entropy[property_id] = {}
        state_to_count = property_to_state_to_count[property_id]
        max_val = max(state_to_count.values())
        for state in state_to_count:
            property_to_state_to_entropy[property_id][state] = get_entropy(state_to_count[state]/max_val)
    return property_to_state_to_entropy


def get_entropy(p):
    return -p*log(p)

def convert_cutpoints_to_output(bins_cutpoints, property_to_entities, class_to_entities: Dict[int, Set[Entity]], property_to_timestamps,
                                folder_path, dataset_name, method_name, vmap_path):
    """
    :param class_to_entities: A dictionary mapping class ids to the set of entities under this class
    :param folder_path: A path for the folder in which the output file is to be saved
    :param dataset_name: The name of the dataset
    :param method_name: The name of the discretization method used
    :return:
    """

    number_of_entities = 0
    states_path = folder_path + "\\" + "states.csv"
    entities_path = folder_path + "\\" + "entities_class_"
    property_to_base = {}
    last_base = 0
    cutpoints = bins_cutpoints
    for key in sorted(cutpoints.keys()):
        property_to_base[key] = last_base
        last_base += len(cutpoints[key])+1

    id_to_name = {}
    try:
        with open(vmap_path) as in_file:
            input = csv.reader(in_file)
            for line in input:
                id = line[0]
                name = line[1]
                if name == "TemporalPropertyName":
                    continue
                else:
                    id_to_name[int(id)] = name
    except FileNotFoundError:
        for property_id in property_to_entities:
            id_to_name[int(property_id)] = "Property_" % (property_id)

    with open(states_path,'w', newline='') as out_file:
        out = csv.writer(out_file)
        out.writerow(["StateID","IntervalClusterID","TemporalPropertyID","TemporalPropertyName","MethodName","Error1",
                           "Entropy","BinID","BinLabel","BinFrom","BinTo","IntervalClusterLabel","IntervalClusterCentroid",
                           "IntervalClusterVariance","IntervalClusterSize"])
        state_id = 0
        for key in sorted(cutpoints.keys()):
            bin_id = 0
            from_val = -(10**5)
            for cutpoint in cutpoints[key]:
                out.writerow([str(state_id),"1",str(key),id_to_name[key],method_name,"0","0",bin_id,"Level%s" % bin_id,from_val,cutpoint,"NoClustering","1","0","0"])
                from_val = cutpoint
                state_id += 1
                bin_id += 1
            out.writerow(
                [str(state_id), "1", str(key), id_to_name[key], method_name, "0", "0", bin_id, "Level%s" % bin_id,
                 from_val, (10**5), "NoClustering", "1", "0", "0"])
            state_id += 1
            bin_id += 1

    for _class in class_to_entities:
        number_of_entities += len(class_to_entities[_class])

    for _class in class_to_entities:
        file_name = method_name + '_Class' + str(_class) + '.txt'
        full_path = folder_path + "\\" + file_name
        karma_path = folder_path + "\\" + "karma_input_" + method_name + '_Class' + str(_class) + '.kcsv'

        with open(full_path, 'w+') as f, open(karma_path, 'w+') as karma_output, open(entities_path + str(_class) +".csv", 'w', newline='') as entities_file:
            ef = csv.writer(entities_file)
            ef.writerow(["id","name"])
            f.write('startToncepts \n')
            f.write('numberOfEntities,' + str(number_of_entities) + '\n')
            karma_output.write('startToncepts \n')
            karma_output.write('numberOfEntities,' + str(number_of_entities) + '\n')
            for _entity in class_to_entities[_class]:
                ef.writerow([str(_entity.entity_id),"Entity%s" % _entity.entity_id])
                f.write(str(_entity.entity_id) + ';\n')

                karma_output.write(str(_entity.entity_id) + ';\n')
                entity_elements = []
                for _property in _entity.properties:

                    for _time_stamp in _entity.properties[_property]:
                        _start_time = _time_stamp.start_point
                        _end_time = _time_stamp.end_point
                        op_id = _time_stamp.value
                        p_id = _property
                        entity_element = [_start_time, _end_time, op_id, p_id]
                        entity_elements.append(entity_element)

                entity_elements = sorted(entity_elements, key=lambda e: e[0])
                for i in range(len(entity_elements)):
                    _entity_element = entity_elements[i]
                    f.write(str(_entity_element[0]) + ',' + str(_entity_element[1]) + ',' +
                            str(_entity_element[2]) + ',' + str(_entity_element[3]))
                    karma_output.write(str(_entity_element[0]) + ',' + str(_entity_element[1]) + ',' +
                            str(property_to_base[_entity_element[3]]+_entity_element[2]) + ',' + str(_entity_element[3]))
                    if i+1!=len(entity_elements):
                        f.write(';')
                        karma_output.write(';')
                f.write('\n')
                karma_output.write('\n')


if __name__ == '__main__':

    test_path = r'D:\test_stuff.txt'
    dataset_path = r'..\..\datasets\SAGender/SAGender.csv'

    m1, m2, m3 = get_maps_from_file(dataset_path, 55)
    d = EqualWidth(4)
    # _m1, _m2, _m3 = d.get_copy_of_maps(m1, m2, m3)
    _m1, _m2, _m3 = d.discretize(m1, m2, m3)
    convert_cutpoints_to_output(_m2, "D:\\", 'SAGender', d.get_discretization_name())
