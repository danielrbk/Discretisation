import csv
import datetime
import sys
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
        lst = []
        path = path.split("/")
        file_id = path[0]
        method_name = path[1].upper()
        abstraction_args = path[2]
        lst.append(method_name)
        lst.append(abstraction_args)
        if len(path) > 3:
            pattern_discovery_name = path[3].upper()
            pattern_discovery_args = path[4]
            lst.append(pattern_discovery_name)
            lst.append(pattern_discovery_args)
            if len(path) > 5:
                lst.append(path[5].upper())
                lst.append(path[6])
        if file_id in file_to_runs:
            file_to_runs[file_id].append(lst)
        else:
            file_to_runs[file_id] = [lst]

    for file_id in file_to_runs:
        first_method(file_to_runs[file_id],root_folder,file_id)
        with open(HAPPY_LOG_PATH, 'a') as f:
            f.write("--------------------\nDate: %s\nDiscretized file %s" % (datetime.datetime.now(),file_id))

    for file_id in file_to_runs:
        second_method(file_to_runs[file_id],root_folder,file_id)


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
            try:
                if not exists(output_path_folder):
                    makedirs(output_path_folder)
                if method_name == "KARMALEGO":
                    discretization_methods.remove(running_configuration)
                    use_karma_lego(input_path, output_path_folder, "TIRPS.csv",args)
                    run_KL(input_path, output_path_folder, *args)
                    continue
                elif discretizable:
                    d: Discretization = running_configuration[-1]
                    d.property_folder = "%s\\%s\\%s" % (root_folder, file_id, "partitions")
                    if not DEBUG_MODE and (exists(output_path_folder + "\\states.csv") or exists(output_path_folder + "\\property%s_cutpoints.temp" % pid)):
                        #discretization_methods.remove(running_configuration)
                        discretization_count += total_properties - 1
                        print("Output files found! Canceling discretization method for this dataset... %s/%s is the new count." % (discretization_count, total_configurations*total_properties))
                        continue
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
                    write_partition(d1,d2,d3,d.bins_cutpoints[pid],output_path_folder,pid)
            except Exception as e:
                print("\n*************EXCPETION THROWN!!!!*************")
                exception_text = "--------------------\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\nError: %s\n" % (
                    datetime.datetime.now(), input_path, output_path_folder, method_name, args, e)
                print(exception_text)
                print("***********************************************\n")
                with open(output_path_folder + "\\error.log", 'w') as f:
                    f.write(exception_text)
                with open(SAD_LOG_PATH, 'a') as f:
                    f.write(exception_text)
                raise
    print("Writing output...")
    configuration_count = 0
    for running_configuration in discretization_methods:
        method_name = running_configuration[0]
        args = running_configuration[1]

        configuration_count += 1
        method_name = running_configuration[0]
        if method_name == "KARMALEGO":
            continue
        args = running_configuration[1]
        print("Outputting method %s, total: %s/%s" % (method_name,configuration_count, total_configurations))
        output_path_folder = "%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args)
        vmap_path = "%s\\%s\\%s" % (root_folder, file_id, "vmap.csv")
        try:
            merge_partitions(output_path_folder,vmap_path,method_name,property_ids,list(class_to_entity_count.keys()),class_to_entity_count, entity_count)
        except Exception as e:
            print("\n*************EXCPETION THROWN WHILE OUTPUTTING!!!!*************")
            exception_text = "--------------------\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\nError: %s\n" % (
                datetime.datetime.now(), input_path, output_path_folder, method_name, args, e)
            print(exception_text)
            print("***********************************************\n")
            with open(output_path_folder + "\\error.log", 'w') as f:
                f.write(exception_text)
            with open(SAD_LOG_PATH, 'a') as f:
                f.write(exception_text)
            raise


def second_method(running_configurations, root_folder, file_id):
    for running_configuration in running_configurations:
        if len(running_configuration) <= 2:
            continue
        method_name = running_configuration[0]
        args = running_configuration[1]
        pattern_discovery = running_configuration[2]
        pattern_discovery_args = running_configuration[3]
        runKFOLD = False
        if len(running_configuration)>4 and running_configuration[4].upper() == "KFOLD":
            runKFOLD = True
            k = running_configuration[5]
            if int(k) == 1:
                runKFOLD = False
        input_path_folder = "%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args)
        output_path_folder = "%s\\%s\\%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args, pattern_discovery, pattern_discovery_args)
        input_paths = []
        for file in listdir(input_path_folder):
            file_name = file
            if "discretized" in file_name:
                input_path = input_path_folder + "\\" + file
                input_paths.append(input_path)
                if not runKFOLD:
                    print("Pattern Discovery on %s" % file_name)
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
                            with open(output_path_folder + "\\error.log", 'w') as j:
                                j.write(exception_text)
                            print("***********************************************\n")
                            f.write(exception_text)
        if runKFOLD:
            kfold_args = pattern_discovery_args.split('_')
            use_kfold(input_paths,output_path_folder + "\\KFOLD\\%s" % k,k,*kfold_args)
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
    files_in_dir = listdir(output_path)
    c = 0
    k = int(k)
    for file in files_in_dir:
        if file.split(".")[-1] == "csv":
            c+=1
    if c != k*2:
        kfold_tirps(input_paths,output_path,k,int(epsilon),int(max_gap),float(vertical_support))
        with open(output_path + "\\" + "finished.log", 'w') as f:
            f.write(
                "----FINISHED!----\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\n" % (
                    datetime.datetime.now(), input_paths, output_path, "KFOLD", [k,epsilon,max_gap,vertical_support]))


if __name__ == '__main__':
    run_methods(sys.argv[1], sys.argv[2:])


