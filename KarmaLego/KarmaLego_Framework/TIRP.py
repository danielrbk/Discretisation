from copy import copy,deepcopy

from KarmaLego.KarmaLego_Framework.TirpMatrix import TirpMatrix
from KarmaLego.KarmaLego_Framework.RelationHandler import RelationHandler
import itertools
import numpy as np

class TIRP (object):

    def __init__(self, first_symbol = None, second_symbol = None, relation = None,label=0):
        self._Artemis_by_entity={}
        if first_symbol is not None and second_symbol is not None and relation is not None:
            self._symbols=[first_symbol, second_symbol]
            self._tirp_matrix = TirpMatrix(relation)
        else:
            self._symbols = []
            self._tirp_matrix = {}

        self._supporting_sequences_by_entity = {}
        self._label=label
        self._name=""

    def get_vertical_support(self):
        return len(self._supporting_sequences_by_entity.items())

    def copy(self):
        """
        create new tirp and copy all current variables
        :return: TIRP,copy of this tirp
        """
        new_tirp = TIRP()
        new_tirp._symbols = copy(self._symbols)
        new_tirp._label=self._label
        new_tirp._tirp_matrix = self._tirp_matrix.copy()
        for entity_id in self._supporting_sequences_by_entity.keys():
            new_tirp._supporting_sequences_by_entity[entity_id] = deepcopy(self._supporting_sequences_by_entity[entity_id])
        for entity_id in self._Artemis_by_entity.keys():
            new_tirp._Artemis_by_entity[entity_id] = deepcopy(self._Artemis_by_entity[entity_id])
        return new_tirp


    def hollow_copy(self):
        """
        create new tirp and copy all current variables
        :return: TIRP,copy of this tirp
        """
        new_tirp = TIRP()
        new_tirp._symbols = copy(self._symbols)
        new_tirp._label=self._label
        new_tirp._name = self._name
        new_tirp._tirp_matrix = self._tirp_matrix.copy()

        return new_tirp

    def get_last_symbol(self):
        """
        returns the last symbol of the tirp
        :return:int, last symbol
        """
        return self._symbols[-1]




    def get_mean_mean_duration(self):
        mean_duration_list=[]
        for entity in self._supporting_sequences_by_entity:
            instances = self._supporting_sequences_by_entity[entity]
            #instances = instances[0]
            start_list = []
            end_list = []
            duration_list = []
            for i, instance in enumerate(instances):
                start_list.extend([x._start_time for x in instance])
                end_list.extend([x._end_time for x in instance])
                min_start_time = min(start_list)
                max_end_time = max(end_list)
                duration = max_end_time - min_start_time
                duration_list.append(duration)
                start_list = []
                end_list = []
            mean_duration = sum(duration_list) / len(duration_list)
            mean_duration_list.append(mean_duration)
        return np.mean(mean_duration_list)


    def calculate_mean_horizontal_support(self):
        """
        calculate the average horizontal support between all the supporting instances
        :return: double - the mean horizontal support value
        """
        num_of_entities=len(self._supporting_sequences_by_entity)
        if num_of_entities==0:
            return 0
        num_of_instances=0
        for entity_id, instances in self._supporting_sequences_by_entity.items():
            num_of_instances=num_of_instances+len(instances)
        mean_horizontal_support=num_of_instances/num_of_entities
        self._mean_horizontal_support=mean_horizontal_support
        return mean_horizontal_support

    def print_tirp(self,path,num_relations):
        """
        printing the TIRP into a file
        :param path: the output path to print the TIRP
        :param num_relations: number of relations used in the mining process
        :return: None - a file with the TIRPs
        """
        rel_object=RelationHandler(num_relations)
        tirp_string=str(len(self._symbols))
        tirp_string=tirp_string+" "
        for sym in self._symbols:
            tirp_string=tirp_string+str(sym)+"-"
        tirp_string = tirp_string + " "
        for rel in self._tirp_matrix._relations:
            tirp_string = tirp_string + rel_object.get_short_description(rel) + "."
        tirp_string = tirp_string +" "
        tirp_string = tirp_string +str(len(self._supporting_sequences_by_entity))+" "
        tirp_string = tirp_string + str(self.calculate_mean_horizontal_support()) +" "
        for entity_id, instances in self._supporting_sequences_by_entity.items():
            tirp_string = tirp_string + str(entity_id) + " "
            for instance in instances:
                for sym in instance:
                    tirp_string = tirp_string + "[" + str(sym.getStartTime()) + "-" + str(sym.getEndTime())+"]"
            tirp_string = tirp_string + " "
        with open(path, 'a') as output_file:
            output_file.write(tirp_string + "\n")

    def get_tirp_name(self,num_relations):
        rel_object = RelationHandler(num_relations)
        if len(self._symbols)== 1:
            return  str(self._symbols[0])
        rel = 0
        name = ''
        for i, j in itertools.combinations(self._symbols, 2):
            name = name + str(i) + rel_object.get_short_description(self._tirp_matrix._relations[rel]) + str(j) + '_'
            rel = rel + 1
        name = name[:-1]
        self._name=name
        return name

    def to_string(self):
        ans=''

        for symbol in self._symbols:
            ans+=str(symbol)+'_'

        ans+=self._tirp_matrix.to_string()

        return ans

