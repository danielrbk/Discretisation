import csv
import datetime
import sys
from typing import List, Dict, Tuple
from os import makedirs
from os.path import exists

from Implementation.AbstractDiscretisation import Discretization
from Implementation.ClassicMethods import Binary, EQF, EQW, KMeans, Persist, SAX
from Implementation.ClassicMethods.Expert import Expert
from Implementation.ClassicMethods.SAX import use_sax
from Implementation.Constants import CLASS_SEPARATOR, FileFormatNotCorrect
from Implementation.InputHandler import get_maps_from_file
from Implementation.OutputHandling.Discretization_Out_Handler import convert_cutpoints_to_output, write_partition, \
    merge_partitions
from Implementation.TD4C.TD4C import TD4C
#from RunKL import run_KL
from RunKL import run_KL

methods_names_to_functions = {"BINARY": Binary.Binary, "EQF": EQF.EqualFrequency, "EQW": EQW.EqualWidth,
                              "KMEANS": KMeans.KMeans, "PERSIST": Persist.Persist, "TD4C": TD4C, "EXPERT": Expert, "SAX": SAX.SAX}


def run_method(input_path, output_path_folder, method_name, args):
    """
    :param input_path: input file
    :param output_path_folder: A path for the folder in which the output file is to be saved
    :param method_name: name for the requested method
    :param args: list of arguments for the requested method
    :return: void
    """
    try:
        with open(r"C:\Users\rejabek\Server\python_happy_log.txt", 'a') as f:
            f.write("--------------------\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\n" % (datetime.datetime.now(),input_path,output_path_folder,method_name,args))

        print(args[0])
        dataset_name = input_path.split('\\')[-1][:-4]
        d = methods_names_to_functions[method_name](*args)
        m1, m2, m3 = get_maps_from_file(input_path, CLASS_SEPARATOR)
        d1, d2, d3 = d.discretize(m1, m2, m3)
        s = d.bins_cutpoints.__str__()
        convert_cutpoints_to_output(d2, output_path_folder, dataset_name, d.get_discretization_name())
        d.write_auxiliary_information(d1, d2, d3, output_path_folder)
        with open(output_path_folder + "\\" + "cut_points.txt", 'w') as f:
            f.write(s)
    except Exception as e:
        with open(r"C:\Users\rejabek\Server\python_error_log.txt", 'a') as f:
            f.write("--------------------\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\nError: %s\n" % (datetime.datetime.now(),input_path,output_path_folder,method_name,args,e))


def run_methods(root_folder, list_of_paths: List[str]):
    # path = file_id/method_name/configs
    file_to_runs: Dict[str, List[Tuple[str, str]]] = {}
    ran = 0
    print(root_folder)
    print(list_of_paths)
    for path in list_of_paths:
        path = path.split("/")
        file_id = path[0]
        method_name = path[1].upper()
        abstraction_args = path[2]
        if len(path) > 3:
            pattern_discovery_args = path[3]
        if file_id in file_to_runs:
            if len(path) > 3:
                file_to_runs[file_id].append((method_name, abstraction_args, pattern_discovery_args))
            else:
                file_to_runs[file_id].append((method_name, abstraction_args))
        else:
            if len(path) > 3:
                file_to_runs[file_id] = [(method_name, abstraction_args, pattern_discovery_args)]
            else:
                file_to_runs[file_id] = [(method_name, abstraction_args)]

    for file_id in file_to_runs:
        first_method(file_to_runs[file_id],root_folder,file_id)

    for file_id in file_to_runs:
        for running_configuration in file_to_runs[file_id]:
            if len(running_configuration) <= 2:
                continue
            method_name = running_configuration[0]
            args = running_configuration[1]
            pattern_discovery_args = running_configuration[2]
            input_path_folder = "%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args)
            output_path_folder = "%s\\%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args, pattern_discovery_args)
            if not exists(output_path_folder):
                makedirs(output_path_folder)
            args = pattern_discovery_args.split("_")
            try:
                run_KL(input_path, output_path_folder + "\\TIRPS.csv", *args)
                with open(output_path_folder + "\\" + "finished.log", 'w') as f:
                    f.write(
                        "----FINISHED!----\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\n" % (
                            datetime.datetime.now(), input_path, output_path_folder, "KarmaLego", args))
                with open(r"C:\Users\rejabek\Server\python_happy_log.txt", 'a') as f:
                    f.write(
                        "--------------------\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\n" % (
                            datetime.datetime.now(), input_path, output_path_folder, "KarmaLego", args))
            except Exception as e:
                with open(r"C:\Users\rejabek\Server\python_sad_log.txt", 'a') as f:
                    f.write(
                        "--------------------\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\nError: %s\n" % (
                            datetime.datetime.now(), input_path, output_path_folder, "KarmaLego", args, e))


def first_method(running_configurations, root_folder, file_id):
    input_path = "%s\\%s\\%s.csv" % (root_folder, file_id, file_id)
    partitions_path = "%s\\%s\\%s" % (root_folder, file_id, "partitions")
    entities_path = "%s\\%s\\%s" % (root_folder, file_id, "entities.csv")
    discretizable = True
    p2e = {}
    c2e = {}
    p2t = {}
    property_ids = []
    class_to_entity_count = {}
    entity_count = 0
    print("Checking partitions...")
    try:
        get_maps_from_file(input_path, entities_path, CLASS_SEPARATOR)
    except FileFormatNotCorrect as e:
        discretizable = False
    with open(partitions_path + "\\properties.csv") as f:
        in_f = csv.reader(f)
        for line in in_f:
            property_ids = [int(x) for x in list(line)]
    with open(partitions_path + "\\class_to_entity_count.csv") as f:
        in_f = csv.reader(f)
        for line in in_f:
            class_to_entity_count[int(line[0])] = int(line[1])
    with open(entities_path) as f:
        in_f = csv.reader(f)
        for line in f:
            entity_count += 1
        entity_count -= 1

    print("Partitions done")
    discretization_methods: List[Tuple(str,str,Discretization)] = []
    for running_configuration in running_configurations:
        method_name = running_configuration[0]
        args = running_configuration[1]
        if method_name == "EXPERT":
            md5 = args.split("_")[0]
            max_gap = args.split("_")[1]
            discretization_methods.append((method_name,args,Expert("%s\\%s\\%s\\%s" % (root_folder,file_id,method_name,md5),max_gap)))
        else:
            discretization_methods.append((method_name, args, methods_names_to_functions[method_name](*args.split("_"))))
    discretization_methods = sorted(discretization_methods, key=lambda x: x[2].get_map_used())
    property_count = 0
    total_properties = len(property_ids)
    discretization_count = 0
    total_configurations = len(discretization_methods)
    for pid in property_ids:
        last_map_used = ""
        p2e = {}
        c2e = {}
        p2t = {}
        for running_configuration in discretization_methods:
            discretization_count += 1
            method_name = running_configuration[0]
            args = running_configuration[1]
            print("                     Discretizing property id %s in method %s, total: %s/%s" % (pid,method_name,discretization_count,total_configurations*total_properties))
            print("                     ------------------------------------------------------")
            output_path_folder = "%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args)
            vmap_path = "%s\\%s\\%s" % (root_folder, file_id, "vmap.csv")
            if not exists(output_path_folder):
                makedirs(output_path_folder)
            if method_name == "KARMALEGO":
                discretization_methods.remove(running_configuration)
                run_KL(input_path, output_path_folder, *args)
                continue
            elif discretizable:
                d: Discretization = running_configuration[-1]
                d.property_folder = "%s\\%s\\%s" % (root_folder, file_id, "partitions")
                if d.get_map_used() != last_map_used:
                    print("***CLEANING MAPS FROM MEMORY***")
                    last_map_used = d.get_map_used()
                    del p2e
                    del c2e
                    del p2t
                    p2e = {}
                    c2e = {}
                    p2t = {}
                d1, d2, d3 = d.discretize_property(p2e, c2e, p2t, pid)
                write_partition(d1,d2,d3,output_path_folder,pid)
    print("Writing output...")
    configuration_count = 0
    for running_configuration in discretization_methods:
        configuration_count += 1
        method_name = running_configuration[0]
        if method_name == "KARMALEGO":
            continue
        args = running_configuration[1]
        print("Outputting method %s, total: %s/%s" % (method_name,configuration_count, total_configurations))
        output_path_folder = "%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args)
        vmap_path = "%s\\%s\\%s" % (root_folder, file_id, "vmap.csv")
        merge_partitions(output_path_folder,vmap_path,method_name,property_ids,class_to_entity_count.keys(),class_to_entity_count,running_configuration[-1].bins_cutpoints, entity_count)



if __name__ == '__main__':
    run_methods(sys.argv[1], sys.argv[2:])


