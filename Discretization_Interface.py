from typing import List, Dict, Tuple

from Implementation.ClassicMethods import Binary, EQF, EQW, Expert, KMeans, Persist, SAX
from Implementation.InputHandler import get_maps_from_file
from Implementation.OutputHandling.Discretization_Out_Handler import convert_cutpoints_to_output
import sys

from Implementation.TD4C.TD4C import TD4C

methods_names_to_functions = {"BINARY": Binary.Binary, "EQF": EQF.EqualFrequency, "EQW": EQW.EqualWidth, "EXPERT": Expert.Expert,
                              "KMEANS": KMeans.KMeans, "PERSIST": Persist.Persist, "SAX": SAX, "TD4C": TD4C}


def run_method(input_path, output_path_folder, method_name, args):
    """
    :param input_path: input file
    :param output_path_folder: A path for the folder in which the output file is to be saved
    :param method_name: name for the requested method
    :param args: list of arguments for the requested method
    :return: void
    """
    print(args[0])
    dataset_name = input_path.split('\\')[-1][:-4]
    d = methods_names_to_functions[method_name](*args)
    m1, m2, m3 = get_maps_from_file(input_path, 55)
    d1, d2, d3 = d.discretize(m1, m2, m3)
    convert_cutpoints_to_output(d2, output_path_folder, dataset_name, d.get_discretization_name())
    d.write_auxiliary_information(d1, d2, d3, output_path_folder)
    with open(output_path_folder + "\\" + "cut_points.txt") as f:
        f.write(d.bins_cutpoints)


def run_methods(root_folder, list_of_paths: List[str]):
    # path = file_id/method_name/configs
    file_to_runs: Dict[str, List[Tuple[str, str]]] = {}
    for path in list_of_paths:
        path = path.split("/")
        file_id = path[0]
        method_name = path[1]
        args = path[2]
        if file_id in file_to_runs:
            file_to_runs[file_id].append((method_name, args))
        else:
            file_to_runs[file_to_runs] = [(method_name, args)]
    for file_id in file_to_runs:
        input_path = "%s\\%s\\%s.csv" % (root_folder, file_id, file_id)
        m1, m2, m3 = get_maps_from_file(input_path, 55)
        for running_configuration in file_to_runs[file_id]:
            method_name = running_configuration[0]
            args = running_configuration[1]
            output_path_folder = "%s\\%s\\%s\\%s" % (root_folder, file_id, method_name, args)
            args = args.split("_")
            d = methods_names_to_functions[method_name](*args)
            d1, d2, d3 = d.discretize(m1, m2, m3)
            convert_cutpoints_to_output(d2, output_path_folder, file_id, d.get_discretization_name())
            d.write_auxiliary_information(d1, d2, d3, output_path_folder)
            with open(output_path_folder + "\\" + "cut_points.txt") as f:
                f.write(d.bins_cutpoints)


if __name__ == '__main__':
    run_method(*sys.argv[1:])

