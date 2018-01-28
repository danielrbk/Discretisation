import csv
import tempfile
import os
from typing import Dict, List
INT_TYPES = ["int", "integer"]
FLOAT_TYPES = ["float", "double", "real", "number"]


def read_csv(path, header_path, out_path):
    header_to_type: Dict[str, type] = {}
    header_to_value_range: Dict[str, any] = {}
    inputs: List[str] = []
    outputs: List[str] = []
    header_names: List[str] = []
    with open(path, encoding='utf_8') as in_file, open(header_path, encoding='utf_8') as header_file, \
            open(out_path, 'w', encoding='utf_8') as out_file:
        #out = csv.writer(out_file)
        out_file.write("@relation %s\n" % os.path.splitext(os.path.basename(out_path))[0])
        headers = csv.reader(header_file)
        extract_header_types(headers, header_to_type, inputs, outputs, header_names)
        data_sheet = csv.reader(in_file)
        header = True
        for line in data_sheet:
            if header:
                header = False
                continue
            for i in range(len(line)):
                header_type: type = header_to_type[header_names[i]]
                value: str = line[i]
                add_value_to_header_ranges(header_to_value_range, header_names[i], header_type, value)
        in_file.seek(0, 0)
        write_headers_to_file(inputs, outputs, header_names, header_to_type, header_to_value_range, data_sheet, out_file)


def extract_header_types(header_reader, header_type_dictionary: Dict[str,type], inputs: List[str], outputs: List[str],
                         header_names: List[str]) -> None:
    """
    Extract the headers of the csv table using a file made by the user mapping each header to its variable type.
    Supported types appear in the top of the file, while resorting to string as a default
    :param header_names: A list to populate with the names of every header
    :param outputs: A list to populate with the headers serving as outputs
    :param inputs: A list to populate with the headers serving as inputs
    :param header_reader: the csv reader of the header file
    :param header_type_dictionary: a dictionary between the header name to its type to populate
    :return:
    """
    for line in header_reader:
        if line[0] == "in":
            for input_header in line[1:]:
                inputs.append(input_header)
        elif line[0] == "out":
            if len(line[1:]) > 1:
                raise Exception("Too many outputs! only one is supported currently")
            for output_header in line[1:]:
                outputs.append(output_header)
        else:
            header = line[0]
            header_names.append(header)
            header_type: str = line[1]
            header_type = header_type.lower()
            if header_type in INT_TYPES:
                header_type_dictionary[header] = int
            elif header_type in FLOAT_TYPES:
                header_type_dictionary[header] = float
            else:
                header_type_dictionary[header] = str

    err_in = []
    err_out = []
    err_msg = ""
    for input_header in inputs:
        if input_header not in header_names:
            err_in.append(input_header)
    for output in outputs:
        if output not in header_names:
            err_out.append(output)
    if len(err_in) > 0:
        err_msg += "The following inputs are not in the headers: %s\n" % err_in
    if len(err_out) > 0:
        err_msg += "The following outputs are not in the headers: %s" % err_out
    if len(err_msg) > 0:
        raise Exception(err_msg)


def write_headers_to_file(inputs: List[str], outputs: List[str], header_names: List[str],
                          header_type_dictionary: Dict[str, type], header_to_value_range: Dict[str, any],
                          data_file, out) -> None:
    for header_name in header_names:
        header_type = header_type_dictionary[header_name]
        l = header_to_value_range[header_name]
        if header_type is int:
            out.write("@attribute %s %s\n" % (header_name, "integer %s" % header_to_value_range[header_name]))
        elif header_type is float:
            out.write("@attribute %s %s\n" % (header_name, "real %s" % header_to_value_range[header_name]))
        else:
            s = ""
            for val in header_to_value_range[header_name]:
                s += val
                s += ", "
            s = s[:-2]
            out.write("@attribute %s {%s}\n" % (header_name, s))
    out.write("@inputs %s\n" % ", ".join(inputs))
    out.write("@outputs %s\n" % outputs[0])
    out.write("@data\n")
    header = True
    for line in data_file:
        if header:
            header = False
            continue
        out.write("%s\n" % ",".join(line))


def add_value_to_header_ranges(header_to_value_range: Dict[str, any],
                               header_name: str, header_type: type, value: str) -> None:
    if header_name not in header_to_value_range:
        if header_type is not str:
            header_to_value_range[header_name] = [float('inf'), float('-inf')]
        else:
            header_to_value_range[header_name] = set()
    if header_type is int or header_type is float:
        num = header_type(value)
        if header_to_value_range[header_name][0] > num:
            header_to_value_range[header_name][0] = num
        elif header_to_value_range[header_name][1] < num:
            header_to_value_range[header_name][1] = num
    else:
        header_to_value_range[header_name].add(value)

path = "C:\my data\\"
with open(path + "manipulationVMAP.csv") as i:
    string = "".join(i.readlines())
    string = string.encode('utf-8')
    for input in ["ISE","SP","DAX","FTSE","NIKKEI","BOVESPA","EU","EM"]:
        for time in [True, False]:
            out = "C:\\Users\\redaniel\Downloads\my data\\discretize_%s" % input
            input_string = "in,%s" % input
            output_string = "out,%s_CLASS" % input
            if time:
                out += "_time"
                input_string += ",Time Stamp"
            out += ".dat"
            input_string += "\n" + output_string + "\n"
            with tempfile.NamedTemporaryFile(delete=False) as f:
                b = input_string.encode('utf-8')
                f.file.write(b)
                f.file.write(string)
            read_csv(path + "manipulations.csv", f.name, out)
            os.remove(f.name)