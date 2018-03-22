from Implementation.ClassicMethods import Binary, EQF, EQW, Expert, KMeans, Persist, SAX
from Implementation.InputHandler import get_maps_from_file
from Implementation.OutputHandling.Discretization_Out_Handler import convert_cutpoints_to_output
import sys


methods_names_to_functions = {"BINARY": Binary.Binary, "EQF": EQF.EqualFrequency, "EQW": EQW, "EXPERT": Expert,
                              "KMEANS": KMeans, "PERSIST": Persist, "SAX": SAX}


def run_method(input_path, output_path_folder, method_name, args):
    """
    :param input_path: input file
    :param output_path_folder: A path for the folder in which the output file is to be saved
    :param method_name: name for the requested method
    :param args: list of arguments for the requested method
    :return: void
    """
    # print(args[0])
    # dataset_name = input_path.splitsplit('\\')[-1][:-4]
    # d = methods_names_to_functions[method_name](*args)
    # print("Reading file...")
    # m1, m2, m3 = get_maps_from_file(input_path, 55)
    # d1, d2, d3 = d.discretize(m1, m2, m3)
    # convert_cutpoints_to_output(d2, output_path_folder, dataset_name, d.get_discretization_name())
    with open(output_path_folder+"\\"+"test_CONNECNT.txt",'w+') as f:
        f.writelines([input_path, '\n', output_path_folder, '\n', method_name, '\n', args])
if __name__ == '__main__':
    run_method(*sys.argv[1:])

