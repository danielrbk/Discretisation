from Implementation.ClassicMethods import Binary, EQF, EQW, Expert, KMeans, Persist, SAX
from Implementation.InputHandler import get_maps_from_file
from Implementation.OutputHandling.Discretization_Out_Handler import convert_cutpoints_to_output
import sys


methods_names_to_functions = {"BINARY": Binary.Binary, "EQF": EQF.EqualFrequency, "EQW": EQW, "EXPERT": Expert, "KMEANS": KMeans,
                              "PERSIST": Persist, "SAX": SAX}


def run_method(input_path, output_path_folder, method_name, args):
    dataset_name = input_path.splitsplit('\\')[-1][:-4]
    d = methods_names_to_functions[method_name](*args)
    print("Reading file...")
    m1, m2, m3 = get_maps_from_file(input_path, 55)
    d1, d2, d3 = d.discretize(m1, m2, m3)
    convert_cutpoints_to_output(d2, output_path_folder, dataset_name, d.get_discretization_name())

if __name__ == '__main__':
    print("981234"[:-4])
    run_method(*sys.argv[1:])

