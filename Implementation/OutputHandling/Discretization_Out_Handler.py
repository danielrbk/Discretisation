from typing import Dict, Set
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.Entity import Entity
from Implementation.InputHandler import get_maps_from_file


def convert_cutpoints_to_output(class_to_entities: Dict[int, Set[Entity]], folder_path, dataset_name, method_name):
    """
    :param class_to_entities: A dictionary mapping class ids to the set of entities under this class
    :param folder_path: A path for the folder in which the output file is to be saved
    :param dataset_name: The name of the dataset
    :param method_name: The name of the discretization method used
    :return:
    """

    number_of_entities = 0

    for _class in class_to_entities:
        number_of_entities += len(class_to_entities[_class])

    for _class in class_to_entities:
        file_name = method_name + '_Class' + str(_class) + '.txt'
        full_path = folder_path + "\\" + file_name
        with open(full_path, 'w+') as f:
            f.write('startToncepts \n')
            f.write('numberOfEntities, ' + str(number_of_entities) + '\n')
            for _entity in class_to_entities[_class]:
                f.write(str(_entity.entity_id) + ';\n')
                entity_elements = []
                for _property in _entity.properties:

                    for _time_stamp in _entity.properties[_property]:
                        _start_time = _time_stamp.time.start_point
                        _end_time = _time_stamp.time.end_point
                        op_id = _time_stamp.value
                        p_id = _property
                        entity_element = [_start_time, _end_time, op_id, p_id]
                        entity_elements.append(entity_element)

                entity_elements = sorted(entity_elements, key=lambda e: e[0])
                for _entity_element in entity_elements:
                    f.write(str(_entity_element[0]) + ',' + str(_entity_element[1]) + ',' +
                            str(_entity_element[2]) + ',' + str(_entity_element[3]) + ';')
                f.write('\n')


if __name__ == '__main__':

    test_path = r'D:\test_stuff.txt'
    dataset_path = r'..\..\datasets\SAGender/SAGender.csv'

    m1, m2, m3 = get_maps_from_file(dataset_path, 55)
    d = EqualWidth(4)
    # _m1, _m2, _m3 = d.get_copy_of_maps(m1, m2, m3)
    _m1, _m2, _m3 = d.discretize(m1, m2, m3)
    convert_cutpoints_to_output(_m2, "D:\\", 'SAGender', d.get_discretization_name())
