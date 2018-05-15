import datetime
import sys
from typing import List, Dict, Tuple
from os import makedirs
from os.path import exists
from Implementation.ClassicMethods import Binary, EQF, EQW, Expert, KMeans, Persist, SAX
from Implementation.InputHandler import get_maps_from_file
from Implementation.OutputHandling.Discretization_Out_Handler import convert_cutpoints_to_output
from Implementation.TD4C.TD4C import TD4C
#from RunKL import run_KL
from RunKL import run_KL

methods_names_to_functions = {"BINARY": Binary.Binary, "EQF": EQF.EqualFrequency, "EQW": EQW.EqualWidth, "EXPERT": Expert.Expert,
                              "KMEANS": KMeans.KMeans, "PERSIST": Persist.Persist, "SAX": SAX, "TD4C": TD4C}

CLASS_SEPERATOR = 55


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
        m1, m2, m3 = get_maps_from_file(input_path, CLASS_SEPERATOR)
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
        input_path = "%s\\%s\\%s.csv" % (root_folder, file_id, file_id)
        discretizable = True
        try:
            m1, m2, m3 = get_maps_from_file(input_path, CLASS_SEPERATOR)
        except:
            discretizable = False
        for running_configuration in file_to_runs[file_id]:
            method_name = running_configuration[0]
            args = running_configuration[1]
            output_path_folder = "%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args)
            if not exists(output_path_folder):
                makedirs(output_path_folder)
            args = args.split("_")
            try:
                if method_name == "KARMALEGO":
                    run_KL(input_path, output_path_folder, *args)
                    pass
                elif discretizable:
                    d = methods_names_to_functions[method_name](*args)
                    d1, d2, d3 = d.discretize(m1, m2, m3)
                    convert_cutpoints_to_output(d2, output_path_folder, file_id, d.get_discretization_name())
                    d.write_auxiliary_information(d1, d2, d3, output_path_folder)
                    with open(output_path_folder + "\\" + "cut_points.txt", 'w') as f:
                        f.write(d.bins_cutpoints.__str__())
                with open(output_path_folder + "\\" + "finished.log", 'w') as f:
                    f.write(
                        "----FINISHED!----\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\n" % (
                            datetime.datetime.now(), input_path, output_path_folder, method_name, args))
                with open(r"C:\Users\rejabek\Server\python_happy_log.txt", 'a') as f:
                    f.write(
                        "--------------------\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\n" % (
                            datetime.datetime.now(), input_path, output_path_folder, method_name, args))
            except Exception as e:
                with open(r"C:\Users\rejabek\Server\python_sad_log.txt", 'a') as f:
                    f.write(
                        "--------------------\nDate: %s\nInput file: %s\nOutput path: %s\nMethod: %s\nArgs: %s\nError: %s\n" % (
                        datetime.datetime.now(), input_path, output_path_folder, method_name, args, e))

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


if __name__ == '__main__':
    run_methods(sys.argv[1], sys.argv[2:])


