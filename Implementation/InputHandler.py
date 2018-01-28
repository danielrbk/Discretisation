from os.path import splitext
from Implementation.ClassicMethods.Expert import Expert
from Implementation.AbstractDiscretisation import Discretization
from Implementation.DataRow import DataRow
from Implementation.Entity import Entity
from typing import Dict, List ,Set
from copy import deepcopy, copy

from Implementation.TD4C.TD4C import TD4C

supported_extensions = [".txt",".csv"]
entities: Dict[int,Entity] = {}


def extract_from_file(file_path, file_extension, class_separator) -> bool:
    with open(file_path) as f:
        try:
            l = f.readline()
            for line in f:
                dr = DataRow.get_data_from_row(line)
                eid = dr.get_entity_id()
                if eid in entities:
                    e = entities[eid]
                else:
                    e = Entity(eid, class_separator)
                    entities[eid] = e
                e.add_time_stamp(dr.get_temporal_property_id(),dr.get_time_stamp())
        except:
            return False
    return True


def receive_file(file_path, class_separator):
    file_extension = splitext(file_path)[1]
    if file_extension not in supported_extensions:
        raise Exception("File extension not supported")
    if not extract_from_file(file_path, file_extension, class_separator):
        raise Exception("File format incorrect")


def discretize_entities(discretizers: List[Discretization]):
    for d in discretizers:
        p2e, c2e, p2t = Entity.get_copy_of_maps()
        d.discretize(p2e, c2e, p2t)
        write_output(c2e)


def write_output(class_to_entities: Dict[int, Set[Entity]]):
    pass


if __name__ == "__main__":
    receive_file("C:\\Users\Daniel Rejabek\Downloads\\a.csv",55)
    id = 0
    for e in entities.values():
        print(e)
    p2e, c2e, p2t = Entity.get_copy_of_maps()
    print(TD4C.Cosine(1, p2e, c2e, p2t))



