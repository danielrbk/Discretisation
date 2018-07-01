import csv
import datetime
import sys
from functools import reduce
from typing import List, Dict, Tuple
from os import makedirs, listdir
from os.path import exists

from Implementation.AbstractDiscretisation import Discretization
from Implementation.ClassicMethods import Binary, EQF, EQW, KMeans, Persist, SAX
from Implementation.ClassicMethods.Expert import Expert
from Implementation.ClassicMethods.SAX import use_sax
from Implementation.Constants import CLASS_SEPARATOR, FileFormatNotCorrect, DEBUG_MODE, HAPPY_LOG_PATH, SAD_LOG_PATH
from Implementation.InputHandler import get_maps_from_file
from Implementation.OutputHandling.Discretization_Out_Handler import convert_cutpoints_to_output, write_partition, \
    merge_partitions
from Implementation.TD4C.TD4C import TD4C
#from RunKL import run_KL
from KarmaLego.Utils.FileUtil import kfold_tirps
from RunKL import run_KL
from karma_to_karmav import karma_to_karmav_format

methods_names_to_functions = {"BINARY": Binary.Binary, "EQF": EQF.EqualFrequency, "EQW": EQW.EqualWidth,
                              "KMEANS": KMeans.KMeans, "PERSIST": Persist.Persist, "TD4C": TD4C, "EXPERT": Expert, "SAX": SAX.SAX}

serversocket = None
accepting_new = {}

def init_connection():
    pass

file_to_runs = {}
karmalego_to_run = {}


def run_methods(root_folder, list_of_paths: List[str], list_of_properties = None):
    # path = file_id/method_name/configs
    ran = 0
    print(root_folder)
    print(list_of_paths)
    for i in range(len(list_of_paths)):
        path = list_of_paths[i]
        properties_to_discretize = [int(x) for x in list_of_properties[i]]
        path = path.split("/")
        file_id = path[0]
        path[1] = path[1].upper()
        abstraction_args = path[2]
        if len(path) > 3:
            pattern_discovery_name = path[3]
            pattern_discovery_args = path[4]
        if file_id in file_to_runs:
            file_to_runs[file_id].append([path[1:],properties_to_discretize])
        else:
            file_to_runs[file_id] = [path[1:],properties_to_discretize]

    while len(file_to_runs) != 0:
        file_id = list(file_to_runs.keys())[0]
        first_method(file_to_runs[file_id],root_folder,file_id)
        with open(HAPPY_LOG_PATH, 'a') as f:
            f.write("--------------------\nDate: %s\nDiscretized file %s" % (datetime.datetime.now(),file_id))
        if len(file_to_runs[file_id]) == 0:
            file_to_runs.pop(file_id)

    for file_id in file_to_runs:
        second_method(file_to_runs[file_id],root_folder,file_id)


def first_method(running_configurations, root_folder, file_id):
    accepting_new[file_id] = False
    input_path = "%s\\%s\\%s.csv" % (root_folder, file_id, file_id)
    partitions_path = "%s\\%s\\%s" % (root_folder, file_id, "partitions")
    entities_path = "%s\\%s\\%s" % (root_folder, file_id, "entities.csv")
    p2e = {}
    c2e = {}
    p2t = {}
    property_ids = []
    class_to_entity_count = {}
    entity_count = 0
    print("Checking partitions...")
    property_to_running_configurations = {}
    entity_count, property_ids = preprocess_dataset(class_to_entity_count, entities_path, entity_count, input_path,
                                                    partitions_path, property_ids)
    for pid in property_ids:
        property_to_running_configurations[pid] = []
    for running_configuration in running_configurations:
        for pid in running_configuration[1]:
            property_to_running_configurations[pid].append(running_configuration[0])
    print("Partitions done")
    accepting_new[file_id] = True

    perform_discretization(file_id, input_path, property_ids,
                           property_to_running_configurations, root_folder, running_configurations)

    del accepting_new[file_id]
    merge_output(class_to_entity_count, entity_count, file_id, property_ids, root_folder, running_configurations)


def merge_output(class_to_entity_count, entity_count, file_id, property_ids, root_folder, running_configurations):
    print("Writing output...")
    configuration_count = 0
    total_configurations = len(running_configurations)
    for running_configuration in running_configurations:
        running_configuration = preprocess_configuration(file_id, root_folder, running_configuration)
        configuration_count += 1
        method_name = running_configuration[0]
        if method_name == "KARMALEGO":
            continue
        args = running_configuration[1]
        print("Outputting method %s, total: %s/%s" % (method_name, configuration_count, total_configurations))
        output_path_folder = "%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args)
        vmap_path = "%s\\%s\\%s" % (root_folder, file_id, "vmap.csv")
        merge_partitions(output_path_folder, vmap_path, method_name, property_ids, class_to_entity_count.keys(),
                         class_to_entity_count, running_configuration[-1].bins_cutpoints, entity_count)


def perform_discretization(file_id, input_path, property_ids,
                           property_to_running_configurations, root_folder, running_configurations):
    total_properties = len(property_ids)
    discretization_count = 0
    current_property_index = -1
    while len(property_to_running_configurations) != 0:
        current_property_index += 1
        if current_property_index == total_properties:
            current_property_index = 0
        pid = property_ids[current_property_index]
        if len(property_to_running_configurations[pid]) == 0:
            continue

        total_configurations = len(running_configurations)
        last_map_used = ""
        p2e = {}
        c2e = {}
        p2t = {}
        running_configuration_indices = []
        property_running_configurations = sorted([(property_to_running_configurations[pid][i], i) for i in
                                                  range(len(property_to_running_configurations[pid]))],
                                                 key=lambda x: methods_names_to_functions[x[0]].get_map_used())
        perform_discretization_for_property(c2e, discretization_count, file_id, input_path, last_map_used, p2e, p2t,
                                            pid, property_running_configurations, root_folder,
                                            running_configuration_indices, total_configurations, total_properties)
        running_configuration_indices = list(reversed(sorted(running_configuration_indices)))
        deleted = 0
        for i in running_configuration_indices:
            del property_to_running_configurations[pid][i - deleted]
            deleted += 1


def perform_discretization_for_property(c2e, discretization_count, file_id, input_path, last_map_used, p2e, p2t, pid,
                                        property_running_configurations, root_folder, running_configuration_indices,
                                        total_configurations, total_properties):
    while len(property_running_configurations) != 0:
        running_configuration = property_running_configurations[-1][0]
        running_configuration_indices.append(property_running_configurations[-1][1])
        # preprocess request to fit constructor format
        running_configuration = preprocess_configuration(file_id, root_folder, running_configuration)

        discretization_count += 1
        method_name = running_configuration[0]
        args = running_configuration[1]
        print("                     Discretizing property id %s in method %s, total: %s/%s" % (
        pid, method_name, discretization_count, total_configurations * total_properties))
        print("                     ------------------------------------------------------")
        output_path_folder = "%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args)
        vmap_path = "%s\\%s\\%s" % (root_folder, file_id, "vmap.csv")
        try:
            if not exists(output_path_folder):
                makedirs(output_path_folder)
            d: Discretization = running_configuration[-1]
            d.property_folder = "%s\\%s\\%s" % (root_folder, file_id, "partitions")
            files_in_output = listdir(output_path_folder)
            s = "property%s_" % pid
            if not DEBUG_MODE and reduce(lambda x, y: (s in x) or (s in y), a):
                print("Output files found! Canceling discretization method for this property in the dataset... ")
            else:
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
                write_partition(d1, d2, d3, output_path_folder, pid)
            property_running_configurations.pop()
        except Exception as e:
            print("\n*************EXCPETION THROWN!!!!*************")
            exception_text = "--------------------\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\nError: %s\n" % (
                datetime.datetime.now(), input_path, output_path_folder, "KarmaLego", args, e)
            print(exception_text)
            print("***********************************************\n")
            with open(SAD_LOG_PATH, 'a') as f:
                f.write(exception_text)
                raise


def preprocess_configuration(file_id, root_folder, running_configuration):
    method_name = running_configuration[0]
    args = running_configuration[1]
    if method_name == "EXPERT":
        md5 = args.split("_")[0]
        max_gap = args.split("_")[1]
        running_configuration = \
            (method_name, args, Expert("%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, md5), max_gap))
    else:
        running_configuration = \
            (method_name, args, methods_names_to_functions[method_name](*args.split("_")))
    return running_configuration


def preprocess_dataset(class_to_entity_count, entities_path, entity_count, input_path, partitions_path, property_ids):
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
    return entity_count, property_ids


def second_method(running_configurations, root_folder, file_id):
    for running_configuration in running_configurations:
        if len(running_configuration) <= 2:
            continue
        method_name = running_configuration[0]
        args = running_configuration[1]
        pattern_discovery = running_configuration[2]
        pattern_discovery_args = running_configuration[3]
        runKFOLD = False
        if len(running_configurations)>4 and running_configurations[4].upper() == "KFOLD":
            runKFOLD = True
            k = running_configurations[5]
            if int(k) == 1:
                runKFOLD = False
        input_path_folder = "%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args)
        output_path_folder = "%s\\%s\\%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args, pattern_discovery, pattern_discovery_args)
        input_paths = []
        for file in listdir(input_path_folder):
            file_name = file
            if "discretized" in file_name:
                print("Pattern Discovery on %s" % file_name)
                input_path = input_path_folder + "\\" + file
                input_paths.append(input_path)
                if not runKFOLD:
                    try:
                        if not exists(output_path_folder):
                            makedirs(output_path_folder)
                        args = pattern_discovery_args.split("_")
                        #try:
                        output_file = "TIRPS_" + file_name
                        use_karma_lego(input_path,output_path_folder,output_file,args)
                        with open(HAPPY_LOG_PATH, 'a') as f:
                            f.write(
                                "--------------------\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\n" % (
                                    datetime.datetime.now(), input_path, output_path_folder, "KarmaLego", args))
                    except Exception as e:
                        with open(SAD_LOG_PATH, 'a') as f:
                            print("\n*************EXCPETION THROWN!!!!*************")
                            exception_text = "--------------------\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\nError: %s\n" % (
                                    datetime.datetime.now(), input_path, output_path_folder, "KarmaLego", args, e)
                            print(exception_text)
                            print("***********************************************\n")
                            f.write(exception_text)
        if runKFOLD:
            use_kfold(input_paths,output_path_folder + "\\KFOLD\\%s" % k,k,*args)
        else:
            with open(output_path_folder + "\\" + "finished.log", 'w') as f:
                f.write(
                    "----FINISHED!----\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\n" % (
                        datetime.datetime.now(), input_path_folder, output_path_folder, "KarmaLego", args))


def use_karma_lego(input_path,output_path_folder,output_file,args):
    class_name = output_file.split("_")[-1].split(".")[0]
    output_name = output_path_folder + "\\" + output_file
    print("     Running KarmaLego")
    if DEBUG_MODE or output_file not in listdir(output_path_folder):
        run_KL(input_path, output_name, *args)
    print("     Converting to KarmaLegoV format")
    folder_out = output_path_folder + "\\KARMALEGOV\\%s" % (class_name)
    if not exists(folder_out):
        makedirs(folder_out)
    karma_to_karmav_format(output_name, folder_out + "\\input.karma")
    print("     Created KarmaLegoV format\n")


def use_kfold(input_paths,output_path,k,epsilon,max_gap,vertical_support):
    if not exists(output_path):
        makedirs(output_path)
    kfold_tirps(input_paths,output_path,int(k),int(epsilon),int(max_gap),float(vertical_support))
    with open(output_path + "\\" + "finished.log", 'w') as f:
        f.write(
            "----FINISHED!----\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\n" % (
                datetime.datetime.now(), input_paths, output_path, "KFOLD", [k,epsilon,max_gap,vertical_support]))


if __name__ == '__main__':
    run_methods(sys.argv[1], sys.argv[2:])


