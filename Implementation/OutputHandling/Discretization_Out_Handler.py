import pandas as pd
import Implementation.AbstractDiscretisation as ad
def convert_cutpoints_to_output(property_to_entities, class_to_entities, property_to_timestamps, cutpoints):
    cutpoints_dict = {}
    cutpoints_df = pd.DataFrame()
    number_of_entities = 0
    for _class in class_to_entities:
        number_of_entities += len(class_to_entities[_class])

    for _class in class_to_entities:
        # Create name for the _class output file
        path = r'~/method_Out_Class' + str(_class) + '.txt'
        with open(path) as f:
            f.write('startToncepts \n')
            f.write('numberOfEntities, ' + number_of_entities + '\n')
            for _entity in class_to_entities[_class]:

