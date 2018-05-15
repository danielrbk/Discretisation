
from KarmaLego.KarmaLego_Framework.RelationHandler import RelationHandler

class SingleKarma(object):


    def __init__(self,epsilon=0, num_relations = 7, max_gap = 50):
        '''
        Constrictor
        :param epsilon: epsilon value used in the Karma stage
        :param num_relations: number of relations used in the Karma stage
        :param max_gap: maximal gap used in the Karma stage
        '''
        self._epsilon = epsilon
        self._max_gap = max_gap
        self._relation_handler_obj = RelationHandler(num_relations)
        self._single_entity_index = {}#same as dharma index in karma only this one holds all pairs for a single entity



    def fit(self, skip_followers,entity ,entity_symbols,var_to_symbols_dic, dharma_index):
        '''
        Run karma algorithom for STI's of a single entity

        :param skip_followers:
        :param entity:
        :param entity_symbols:
        :param var_to_symbols_dic:
        :param dharma_index:
        :return:
        '''

        time_intervals_length = len(entity_symbols)
        for sym_ti1_index in range(0, time_intervals_length - 1):
            for sym_ti2_index in range(sym_ti1_index + 1, time_intervals_length):
                sym_ti1 = entity_symbols[sym_ti1_index]
                sym_ti2 = entity_symbols[sym_ti2_index]

                s2_minus_e1 = sym_ti2._start_time - sym_ti1._end_time

                # max gap reached, no need to proceed with the check.
                if s2_minus_e1 > self._max_gap:
                    break

                if sym_ti1._symbol == sym_ti2._symbol:
                    continue

                if skip_followers == True and abs(int(sym_ti1._symbol) - int(sym_ti2._symbol)) == 1:
                    if var_to_symbols_dic[str(sym_ti1._symbol)] == var_to_symbols_dic[str(sym_ti2._symbol)]:
                        continue

                relation = self._relation_handler_obj.check_relation(sym_ti1, sym_ti2, self._epsilon, self._max_gap);
                symbols_key = (sym_ti1._symbol, sym_ti2._symbol)

                if relation != RelationHandler.RELATION_NOT_DEFINED:

                    if self.is_pair_exist(relation,entity,sym_ti1,sym_ti2,dharma_index):#if pair exists in dhrama it means the pair is above the threshold

                        if relation == 6:  # check if the opposite key for equal already exist
                            opposite_key = (sym_ti2._symbol, sym_ti1._symbol)
                            if opposite_key in self._single_entity_index.keys() and relation in self._single_entity_index[opposite_key].keys():
                                continue
                        if symbols_key not in self._single_entity_index.keys():
                            self._single_entity_index[symbols_key] = {relation: {entity: [[sym_ti1, sym_ti2]]}}

                        elif relation not in self._single_entity_index[symbols_key].keys():
                            self._single_entity_index[symbols_key].update({relation: {entity: [[sym_ti1, sym_ti2]]}})

                        elif entity not in self._single_entity_index[symbols_key][relation].keys():
                            self._single_entity_index[symbols_key][relation].update({entity: [[sym_ti1, sym_ti2]]})

                        else:
                            self._single_entity_index[symbols_key][relation][entity].append([sym_ti1, sym_ti2])
                else:
                    continue


    def is_pair_exist(self, relation, entity_id, sym_ti_a, sym_ti_b,dharma_index):
        """

        check if a given STI pair exist for Symbol A and SymbolB relation in a entity
        corresponding to the given entity id.

        :param symbol_a: first symbol
        :param symbol_b: second symbol
        :param relation: relation between first symbol and second symbol
        :param entity_id: the entity id that need to be checked if contains the given STIs.
        :param sym_ti_a: first symbolic interval
        :param sym_ti_b: second symbolic interval
        :param dharma_index: the index built in krama stage is used to check if a given pair is above the threshold - all keys in dharma_index are above the threshold
        :return: true if found, false otherwise
        """

        symbols_key = (sym_ti_a._symbol, sym_ti_b._symbol)

        if symbols_key not in dharma_index.keys():
            return False

        if relation not in dharma_index[symbols_key].keys():
            return False

        if entity_id not in dharma_index[symbols_key][relation].keys():
            return False

        for pair in dharma_index[symbols_key][relation][entity_id]:
            if pair[0] == sym_ti_a and pair[1] == sym_ti_b:
                return True

        return False


