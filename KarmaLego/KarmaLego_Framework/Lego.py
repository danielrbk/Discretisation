import itertools
from copy import copy
import os

from KarmaLego.KarmaLego_Framework.LegoTree import LegoTreeNode
from KarmaLego.KarmaLego_Framework.TIRP import TIRP

class Lego(object):

    def __init__(self, karma,max_tirp_length=5):
        self._karma = karma
        self.frequent_tirps = []
        self._max_tirp_length=max_tirp_length
        self.tirps_tree_root = LegoTreeNode(None)

    def fit(self):
        """
        creating two-sized tirps and send them to extend-tirp
        finaly all frequrnt tirps are created
        :return: None
        """
        frequent_symbol_pairs = self._karma.get_frequent_symbol_pairs()
        i = 1
        for symbol_pair in frequent_symbol_pairs:
            print("%s/%s" % (i,len(frequent_symbol_pairs)))
            i += 1
            symbol1 = symbol_pair[0]
            symbol2 = symbol_pair[1]
            symbols_relations = self._karma.get_relations_for_two_symbols(symbol1, symbol2)
            if not symbols_relations:
                continue
            for relation in symbols_relations:
                new_tirp= self.init_tirp(first_symbol=symbol1, second_symbol=symbol2, relation=relation)
                self.tirps_tree_root.add_node(self.extend_tirp(new_tirp))
        print('Lego fit complete')

    def init_tirp(self, first_symbol, second_symbol, relation):
        """

        :param first_symbol: int, the first symbol in the tirp
        :param second_symbol: int, the second symbol in the tirp
        :param relation: the relation between the two symbols
        :return: TIRP, the new tirp
        """

        new_tirp = TIRP(first_symbol=first_symbol, second_symbol=second_symbol, relation=relation,label=self._karma._label)
        new_tirp._supporting_sequences_by_entity = self._karma.get_all_pairs_mapped_by_entity_id(first_symbol, second_symbol, relation);
        return new_tirp

    def extend_tirp(self, tirp):
        """
         extending recursively the tirp and appending the frequent tirps to self.frequent_tirps
         :param tirp: TIRP, the tirp to extend
         :return: None
        """
        rootNode = LegoTreeNode(tirp)

        self.frequent_tirps.append(tirp)
        relevent_entries_in_dharma = self._karma.get_relevent_entries_in_index_by_last_symbol(tirp.get_last_symbol())

        for (last_symbol, new_symbol), relations in relevent_entries_in_dharma.items():

            for relation in relations.keys():
                candidates = self.generate_candidats(tirp, relation)

                for candidate_relations in candidates:
                    new_tirp = self.extend_single_tirp(tirp, new_symbol, candidate_relations)
                    if new_tirp.get_vertical_support() >= len(self._karma._entities_map)*self._karma._min_ver_support:
                        if len(new_tirp._symbols)<self._max_tirp_length:
                            rootNode.add_node(self.extend_tirp(new_tirp))

        return rootNode

    def generate_candidats(self, tirp, relation):
        """
        generate the relations candidats for the new symbol,new relation column in TirpMatrix
        :param tirp: TIRP, the base TIRP to extend
        :param relation: int, the relation between the new symbol and the last symbol in the tirp
        :return: candidats, list of int , the relations between the new symbol and the current symbols in the tirp
        """
        # TODO use symbol to minimize candidates by query karma if symbols and relation exist/relevant? ans: we use only existing relations between the symbols
        candidates = self.generate_candidates_helper(tirp._tirp_matrix.get_all_direct_relations(), relation, len(tirp._symbols) - 2)
        #adding the relation between the new symbol and the last symbol for each candidat
        for can in candidates:
            can.append(relation)
        return candidates

    def generate_candidates_helper(self, tirp_last_relation_column, first_relation, index):
        """
        generate a list of candidats relations for the new symbol without the relation between the new symbol and the last symbol in the tirp
        :param tirp_last_relation_column: list of int, the last relation column in the current TirpMatrix
        :param first_relation: int, the relation between the new symbol and pervious symbol of the tirp, starts with the last symbol and ends with the first symbol
        :param index: int, the index of the current relation to check in the tirp_last_relation_column, starts with the last index and ends with the first
        :return: ans: list of candidates, each candidat is array of int
        """
        ans = []

        if index < 0:
            ans.append([])
            return ans

        transitivity_list = self._karma._relation_handler_obj.get_transitivity_list(tirp_last_relation_column[index], first_relation)

        for relation in transitivity_list:
            results = self.generate_candidates_helper(tirp_last_relation_column, relation, (index - 1))
            for res in results:
                res.append(relation)
                ans.append(res)
        return ans

    def extend_single_tirp(self, tirp, new_symbol, new_relations):
        """
        first extracting the sti pairs that match the relation between the new symbol and the last symbol
        check if the pairs create a valid sti sequence (all relation match) if yes append the new sti else remove the entity
        from the supporting instances
        :param tirp: TIRP, the current tirp to extend
        :param new_symbol: int, the new symbol to extend the tirp
        :param new_relations: the candidate relations for the tirp
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
                new_pairs = self._karma.get_pairs(new_tirp._symbols[-2],
                                                  new_tirp._symbols[-1],
                                                  new_tirp._tirp_matrix.get_relation(symbols_size - 2, symbols_size - 1),
                                                  entity_id,
                                                  sequence[-1])
                for pair in new_pairs:
                    if self.is_sequence_valid(entity_id, original_sequence, new_tirp._tirp_matrix, pair[1]):
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

    def is_sequence_valid(self, entity_id, stis_sequence, tirp_matrix, candidate_for_append_sti):
        """
        :param entity_id: the entity id that the sequence of stis belong to
        :param stis_sequence: Symbolic Time Intervals sequence
        :param tirp_matrix: Tirp Matrix of relation corresponding to the given sequence combined with the candidate STI.
        :param candidate_for_append_sti: Candidate STI to check if holds all relations with the given STIs sequence
        :return: True if holds all relations, False otherwise
        """

        for index in range(0, len(stis_sequence)):
            if not self._karma.is_pair_exist(tirp_matrix.get_relation(index, tirp_matrix._size), entity_id, stis_sequence[index], candidate_for_append_sti):
                return False

        return True

    def remove_by_indices(self, array, indices):
        """
        remove the unrelevant sequence from the supporting_sequences_by_entity
        :param array: array of intervals 
        :param indices: indexes to remove
        :return: None
        """
        offset = 0
        for index in indices:
            array.pop(index - offset)
            offset += 1

    def print_frequent_tirps(self,path):
        """
        printing all the frequent TIRPs into a file
         :param path: the output path to print the TIRP
        :return: None - a file with the TIRPs
        """
        try:
            os.remove(path)
        except OSError:
            pass
        for tirp in self.frequent_tirps:
            tirp.print_tirp(path,self._karma._num_relations)
