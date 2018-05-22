import csv
from typing import Dict, Set

from Implementation.AbstractDiscretisation import Discretization
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.Entity import Entity
from Implementation.InputHandler import get_maps_from_file


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
                        _start_time = _time_stamp.time.start_point
                        _end_time = _time_stamp.time.end_point
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
