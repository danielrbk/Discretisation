
import itertools
from copy import copy
import os

from KarmaLego.KarmaLego_Framework.LegoTree import LegoTreeNode
from KarmaLego.KarmaLego_Framework.TIRP import TIRP
from KarmaLego.KarmaLego_Framework.Lego import Lego
from KarmaLego.KarmaLegoCD.PredictiveTIRP import PredictiveTIRP
from KarmaLego.KarmaLegoCD.TIRPsFeatureSelection import TIRPFeatureSelection
from KarmaLego.KarmaLego_Framework.TIRPsFeatureExraction import TIRPsFeatureExtraction

class NewLego(Lego):

    def __init__(self, karma_a,karma_b,min_vs_gap, alpha, weights,max_tirp_length=5,max_num_of_levels=2):
        self._karma_a = karma_a
        self._karma_b=karma_b
        self._predictive_tirps = []
        self._max_tirp_length=max_tirp_length
        self._max_num_of_levels=max_num_of_levels
        self.tirps_tree_root = LegoTreeNode(None)
        self._fs_obj=TIRPFeatureSelection(min_vs_gap, alpha, weights)



    def fit(self):
        """
        creating two-sized tirps and send them to extend-tirp
        finaly all frequrnt tirps are created
        we use here the frequent symbols from the 2 clases
        :return: None
        """
        frequent_symbols_classes=list(set(self._karma_a._frequent_symbols+self._karma_b._frequent_symbols))
        for symbol1 in sorted(frequent_symbols_classes):
            for symbol2 in sorted(frequent_symbols_classes):
                symbols_relations_a=self._karma_a.get_relations_for_two_symbols(symbol1, symbol2)
                symbols_relations_b = self._karma_b.get_relations_for_two_symbols(symbol1, symbol2)
                symbols_relations_classes=list(set(symbols_relations_a+symbols_relations_b))
                if not symbols_relations_classes:
                    continue
                for relation in symbols_relations_classes:
                    new_tirp= self.init_tirp(first_symbol=symbol1, second_symbol=symbol2, relation=relation)
                    self.tirps_tree_root.add_node(self.extend_tirp(new_tirp))
        print('NewLego fit complete')



    def init_tirp(self, first_symbol, second_symbol, relation):
        """

        :param first_symbol: int, the first symbol in the tirp
        :param second_symbol: int, the second symbol in the tirp
        :param relation: the relation between the two symbols
        :return: TIRP, the new tirp
        """

        new_tirp_a = TIRP(first_symbol=first_symbol, second_symbol=second_symbol, relation=relation)
        new_tirp_a._supporting_sequences_by_entity = self._karma_a.get_all_pairs_mapped_by_entity_id(first_symbol, second_symbol, relation)
        new_tirp_b = TIRP(first_symbol=first_symbol, second_symbol=second_symbol, relation=relation)
        new_tirp_b._supporting_sequences_by_entity = self._karma_b.get_all_pairs_mapped_by_entity_id(first_symbol,second_symbol,relation)
        new_tirp=PredictiveTIRP(new_tirp_a,new_tirp_b)
        return new_tirp

    def extend_tirp(self, p_tirp,current_level=2):
        """
         extending recursively the tirp and appending the frequent tirps to self.frequent_tirps
         :param tirp: TIRP, the tirp to extend
         :return: None
        """

       # rootNode = LegoTreeNode(p_tirp)

        c_a_vs=(p_tirp._tirp_a.get_vertical_support()/len(self._karma_a._entities_map))
        c_b_vs=(p_tirp._tirp_b.get_vertical_support()/len(self._karma_b._entities_map))
        max_vs=max(c_a_vs,c_b_vs)
        if max_vs<self._karma_a._min_ver_support:
            return
        isPredictive,score=self._fs_obj.fit(p_tirp._tirp_a,p_tirp._tirp_b,c_a_vs,c_b_vs,self._karma_a._entities_map.keys(),self._karma_b._entities_map.keys())

        if isPredictive:
            p_tirp._score=score
            self._predictive_tirps.append(p_tirp)
            if current_level>=self._max_num_of_levels:
                return


        relevent_entries_in_dharma_a = self._karma_a.get_relevent_entries_in_index_by_last_symbol(p_tirp._tirp_a.get_last_symbol())
        relevent_entries_in_dharma_b = self._karma_b.get_relevent_entries_in_index_by_last_symbol(p_tirp._tirp_b.get_last_symbol())

        keys=set(list(relevent_entries_in_dharma_a.keys())+list(relevent_entries_in_dharma_b.keys()))

        relations_a=[list(relations.keys()) for (last_symbol, new_symbol), relations in relevent_entries_in_dharma_a.items()]
        relations_b = [list(relations.keys()) for (last_symbol, new_symbol), relations in relevent_entries_in_dharma_b.items()]
        relations_a_final=[]
        for x in relations_a:
            relations_a_final.extend(x)
        relations_b_final = []
        for x in relations_b:
            relations_b_final.extend(x)
        relations=list(set( relations_a_final+relations_b_final))

        for (last_symbol, new_symbol) in keys:

            for relation in relations:
                candidates = self.generate_candidats(p_tirp._tirp_a, relation,self._karma_a)

                for candidate_relations in candidates:
                    new_tirp_a = self.extend_single_tirp(p_tirp._tirp_a, new_symbol, candidate_relations,self._karma_a)
                    new_tirp_b = self.extend_single_tirp(p_tirp._tirp_b, new_symbol, candidate_relations,self._karma_b)
                    new_tirp = PredictiveTIRP(new_tirp_a, new_tirp_b)
                    if len(new_tirp_a._symbols)<self._max_tirp_length:
                        self.extend_tirp( new_tirp,current_level=current_level+1)

        #return rootNode
    def generate_candidats(self, tirp, relation,karma):
        """
        generate the relations candidats for the new symbol,new relation column in TirpMatrix
        :param tirp: TIRP, the base TIRP to extend
        :param relation: int, the relation between the new symbol and the last symbol in the tirp
        :param karma: Karma object for using the relation handler
        :return: candidats, list of int , the relations between the new symbol and the current symbols in the tirp
        """
        # TODO use symbol to minimize candidates by query karma if symbols and relation exist/relevant? ans: we use only existing relations between the symbols
        candidates = self.generate_candidates_helper(tirp._tirp_matrix.get_all_direct_relations(), relation, len(tirp._symbols) - 2,karma)
        #adding the relation between the new symbol and the last symbol for each candidat
        for can in candidates:
            can.append(relation)
        return candidates

    def generate_candidates_helper(self, tirp_last_relation_column, first_relation, index,karma):
        """
        generate a list of candidats relations for the new symbol without the relation between the new symbol and the last symbol in the tirp
        :param tirp_last_relation_column: list of int, the last relation column in the current TirpMatrix
        :param first_relation: int, the relation between the new symbol and pervious symbol of the tirp, starts with the last symbol and ends with the first symbol
        :param index: int, the index of the current relation to check in the tirp_last_relation_column, starts with the last index and ends with the first
        :param karma: Karma object for using the relation handler
        :return: ans: list of candidates, each candidat is array of int
        """
        ans = []

        if index < 0:
            ans.append([])
            return ans

        transitivity_list = karma._relation_handler_obj.get_transitivity_list(tirp_last_relation_column[index], first_relation)

        for relation in transitivity_list:
            results = self.generate_candidates_helper(tirp_last_relation_column, relation, (index - 1),karma)
            for res in results:
                res.append(relation)
                ans.append(res)
        return ans

    def extend_single_tirp(self, tirp, new_symbol, new_relations,karma):
        """
        first extracting the sti pairs that match the relation between the new symbol and the last symbol
        check if the pairs create a valid sti sequence (all relation match) if yes append the new sti else remove the entity
        from the supporting instances
        :param tirp: TIRP, the current tirp to extend
        :param new_symbol: int, the new symbol to extend the tirp
        :param new_relations: the candidate relations for the tirp
        :param karma: Karma object for checking the supporting instances
        :return: TIRP, the new extended tirp
        """
        new_tirp = tirp.copy()
        new_tirp._symbols.append(new_symbol)
        new_tirp._tirp_matrix.extend(new_relations)

        symbols_size = len(new_tirp._symbols)

        entities_to_remove = []

        for entity_id in new_tirp._supporting_sequences_by_entity.keys():

            new_sequences = []
            remove_indices = []

            for current_index in range(0, len(new_tirp._supporting_sequences_by_entity[entity_id])):
                sequence = new_tirp._supporting_sequences_by_entity[entity_id][current_index]
                original_sequence = copy(sequence)
                extended = False
                new_pairs = karma.get_pairs(new_tirp._symbols[-2],
                                                  new_tirp._symbols[-1],
                                                  new_tirp._tirp_matrix.get_relation(symbols_size - 2, symbols_size - 1),
                                                  entity_id,
                                                  sequence[-1])
                for pair in new_pairs:
                    if self.is_sequence_valid(entity_id, original_sequence, new_tirp._tirp_matrix, pair[1],karma):
                        if not extended:
                            sequence.append(pair[1])
                            extended = True
                        else:
                            new_sequence = copy(original_sequence)
                            new_sequence.append(pair[1])
                            new_sequences.append(new_sequence)

                if not extended:
                    remove_indices.append(current_index)

            self.remove_by_indices(new_tirp._supporting_sequences_by_entity[entity_id], remove_indices)
            new_tirp._supporting_sequences_by_entity[entity_id] = new_tirp._supporting_sequences_by_entity[entity_id]+new_sequences

            if len(new_tirp._supporting_sequences_by_entity[entity_id]) == 0:
                entities_to_remove.append(entity_id)

        for entity_id in entities_to_remove:
            new_tirp._supporting_sequences_by_entity.pop(entity_id)

        return new_tirp

    def is_sequence_valid(self, entity_id, stis_sequence, tirp_matrix, candidate_for_append_sti,karma):
        """
        :param entity_id: the entity id that the sequence of stis belong to
        :param stis_sequence: Symbolic Time Intervals sequence
        :param tirp_matrix: Tirp Matrix of relation corresponding to the given sequence combined with the candidate STI.
        :param candidate_for_append_sti: Candidate STI to check if holds all relations with the given STIs sequence
        :param karma: Karma object for checking if the pair exist in dharma index
        :return: True if holds all relations, False otherwise
        """

        for index in range(0, len(stis_sequence)):
            if not karma.is_pair_exist(tirp_matrix.get_relation(index, tirp_matrix._size), entity_id, stis_sequence[index], candidate_for_append_sti):
                return False

        return True

    def print_predictive_tirps(self,path_a,path_b):
        """
        prints the predictive tirps for each class
        :param path_a: the output path to print the TIRPs for class a
        :param path_b: the output path to print the TIRPs for class b
        :return:  None - 2 files with the TIRPs
        """
        tirps_a=[tirp._tirp_a for tirp in self._predictive_tirps]
        tirps_b=[tirp._tirp_b for tirp in self._predictive_tirps]
        self.print_class_tirps(tirps_a,path_a)
        self.print_class_tirps(tirps_b, path_b)

    def print_class_tirps(self,tirps,path):
        """
        printing the class tirps into a file
         :param path: the output path to print the TIRPs
        :return: None - a file with the TIRPs
        """
        try:
            os.remove(path)
        except OSError:
            pass
        for tirp in tirps:
            tirp.print_tirp(path,self._karma_a._num_relations)

