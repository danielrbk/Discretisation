from typing import Dict, List, Set, Tuple
from Implementation.Entity import Entity
from Implementation.ClassicMethods.EQF import  EqualFrequency
from Implementation import InputHandler
import pandas as pd
import Implementation.AbstractDiscretisation as ad
from Implementation.InputHandler import get_maps_from_file


def convert_cutpoints_to_output(property_to_entities, class_to_entities: Dict[int, Set[Entity]], property_to_timestamps
                                ):
    cutpoints_dict = {}
    cutpoints_df = pd.DataFrame()
    number_of_entities = 0

    for _class in class_to_entities:
        number_of_entities += len(class_to_entities[_class])

    for _class in class_to_entities:
        counter = 0
        # Create name for the _class output file
        path = r'/home/Karish/method_Out_Class' + str(_class) + '.txt'
        with open(path, 'w+') as f:
            f.write('startToncepts \n')
            f.write('numberOfEntities, ' + str(number_of_entities) + '\n')
            for _entity in class_to_entities[_class]:
                if counter == 1:
                    break
                print("ENTITTY ", _entity.entity_id)
                f.write(str(_entity.entity_id) + ';\n')
                entity_elements = []
             #   print(_entity.property_to_timestamps.keys())
                for _property in _entity.property_to_timestamps:
                 #   print(_property)

               ##     print(len(_entity.property_to_timestamps))

                    for _time_stamp in _entity.property_to_timestamps[_property]:

                #        print(_time_stamp.value)

                        _start_time = _time_stamp.time.start_point
                        _end_time = _time_stamp.time.end_point
                        op_id = _time_stamp.value
                        p_id = _property
                        entity_element = [_start_time, _end_time, op_id, p_id]
                        entity_elements.append(entity_element)
                    # entity_elements = []
                    # entity_elements.append(_property)

                entity_elements = sorted(entity_elements, key=lambda e: e[0])
             #   print(entity_elements)
                for _entity_element in entity_elements:
                   # print(entity_element)
                    f.write(str(_entity_element[0]) + ',' + str(_entity_element[1]) + ',' +
                            str(_entity_element[2]) + ',' + str(_entity_element[3]) + ';')
                   # f.write(str(_entity_element))
                f.write('\n')
                counter +=1


if __name__ == '__main__':
    import os

    # dirpath = os.path.dirname(__file__)
    # print(dirpath)
    test_path = r'/home/Karish/test_files/test_stuff.txt'
    dataset_path = r'../../datasets/SAGender/SAGender.csv'
    #dataset_path = r'../../datasets/Test_Dataset.csv'

    m1, m2, m3 = get_maps_from_file(dataset_path, 55)
    d = EqualFrequency(3)
    _m1, _m2, _m3 = d.get_copy_of_maps(m1, m2, m3)
    convert_cutpoints_to_output(_m1, _m2, _m3)
    # with open(test_path, 'w+') as f:
    #     f.write("This is a test file")
