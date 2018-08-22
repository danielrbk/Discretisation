from typing import Dict


def load_discretized_file(curr_file):
    entity_to_records = {}
    with open(curr_file) as f:
        i = 0
        for line in f:
            if i == 1:
                break
            i += 1
            continue
        i = 0
        even = True
        eid = 0
        for line in f:
            if even:
                eid = int(line.rstrip()[:-1])
                entity_to_records[eid] = []
                even = False
            else:
                records = [[int(y) for y in x.split(",")] for x in line.rstrip().split(";")[:-1]]
                entity_to_records[eid] = records
                even = True
    return entity_to_records


def write_discretized_file(d: Dict, out_file):
    with open(out_file,'w') as o:
        o.writelines(["startToncept\n","numberOfEntitites,%s\n" % len(list(d.keys()))])
        for key in sorted(d.keys()):
            o.write("%s;\n" % key)
            new_line = ";".join([",".join([str(y) for y in x]) for x in d[key]]) + ";\n"
            o.write(new_line)


def merge(file1,file2,out_file):
    e2r1 = load_discretized_file(file1)
    e2r2 = load_discretized_file(file2)
    new_e2r = {}
    keys1 = set(e2r1.keys())
    keys2 = set(e2r2.keys())
    shared_keys = list(keys1.intersection(keys2))
    for key in keys1.difference(shared_keys):
        new_e2r[key] = e2r1[key]
    for key in keys2.difference(shared_keys):
        new_e2r[key] = e2r2[key]
    for key in shared_keys:
        new_e2r[key] = e2r1[key] + e2r2[key]
        new_e2r[key] = sorted(new_e2r[key],key=lambda x:(x[0],x[1],x[3],x[2]))
    write_discretized_file(new_e2r,out_file)

if __name__ == "__main__":
    merge(r"D:\Rejabek\test\f1.txt",r"D:\Rejabek\test\f2.txt",r"D:\Rejabek\test\out.txt")