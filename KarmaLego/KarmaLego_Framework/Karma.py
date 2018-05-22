import operator
from itertools import chain
from KarmaLego.KarmaLego_Framework.RelationHandler import RelationHandler
from KarmaLego.KarmaLego_Framework.SymbolicTimeInterval import SymbolicTimeInterval
import logging

class Karma(object):

    def __init__(self,min_ver_support,epsilon=0,num_relations=7,max_gap=50,label=0):
        self._min_ver_support=min_ver_support
        self._epsilon=epsilon
        self._num_relations = num_relations
        self._max_gap=max_gap
        self._entities_map={}
        self._relation_handler_obj=RelationHandler(num_relations)
        self._dharma_index={}
        self._symbolic_interval_start_point = 0
        self._label=label

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
                            datefmt='%d-%m-%Y %H:%M:%S')

        self._logger = logging.getLogger('Karma')
        self._logger.setLevel(logging.INFO)

    def fit(self,file_path,num_comma=3,num_of_bins=3,skip_followers=False,symbol_type='int',min_vertical_support_for_trim=0):
        """
        :param file_path: string, the path to the symbolic time intervals file
        :param skip_followers:  bool,decide if to skip 2 followers symbols (from the same temporal variable)
        :param num_of_bins: integer ,the number of bins/symbols that was used for the temporal abstraction process
        :return:
        """
        self._logger.debug('start fit')

        self.parse_kml_input(file_path,num_comma,symbol_type) # general parser
        self._logger.debug('done loading file')

        self.build_karma_index(skip_followers, num_of_bins)
        self._logger.debug('done building karma index')

        if min_vertical_support_for_trim==0:
            min_vertical_support_for_trim=self._min_ver_support
        self.trim_karma_index_base_on_support(min_vertical_support_for_trim)
        self._logger.debug('done fit')

    def parse_temporal_var_dict(self,file_path):
        """
        The function constructs the mapping from symbols to the symbols they belong to.
        It stores the mapping inside self object that will be later used to skip following symbols
        belonging to the same feature.
        :param file_path: string, the path to the symbolic time intervals file
        :return: nothin
        """
        curr_row_index = 0
        self._var_to_symbols = {}
        with open(file_path, newline='') as f:
            next(f)
            curr_row_index+=1
            for raw_line in f:
                line = raw_line.rstrip().split(",")
                curr_row_index+=1
                if "numberOfEntities" not in line:
                    if line[len(line)-1].isdigit():
                        var_id = line[0]
                        #self._var_to_symbols[var_id] = []
                    else:
                        symbol = line[2]
                        self._var_to_symbols[symbol] = []
                        self._var_to_symbols[symbol].append(var_id)
                else:
                    self._symbolic_interval_start_point = curr_row_index
                    break



    def sort_str_int(self,x ):
        return (x._start_time,x._end_time,float(x._symbol))


    def parse_file_into_symbolic_time_intervals_parts(self, file_path, start_index,symbol_type,num_comma):
        """
        parse the file to a map of entities with their symbolic time intervals
        remove relevant symbols
        sort the symbolic time intervals in a lexicographic order
        :param file_path: string, the path to the symbolic time intervals file
        :param start_index: int, the row from which to parse the symbolic time intervals
        :return: nothing
        """
        symbols_map={}
        with open(file_path) as f:
            lines = f.readlines()[start_index:]
        for i in range(0,len(lines),2):
            entity_symbols=[]
            entity_id=int(lines[i].replace(";",""))
            sym_ti_ls = lines[i+1].split(";")
            for sym_ti in sym_ti_ls[:-1]:
                parts=sym_ti.split(",")
                st=int(parts[0])
                et=int(parts[1])
                symbol = parts[num_comma]
                sym_ti_obj=SymbolicTimeInterval(start_time=st, end_time=et, symbol=symbol)
                if entity_id not in self._entities_map:
                    self._entities_map[entity_id]=[sym_ti_obj]
                else:
                    self._entities_map[entity_id].append(sym_ti_obj)
                if symbol not in symbols_map:
                    symbols_map[symbol]=1
                    entity_symbols.append(symbol)
                elif symbol not in entity_symbols:
                    symbols_map[symbol] = symbols_map[symbol] +1
                    entity_symbols.append(symbol)
        num_of_entitites=len(self._entities_map)
        unrelevent_symbols=[sym for sym in symbols_map if symbols_map[sym]<(num_of_entitites*self._min_ver_support)]
        self._frequent_symbols=[sym for sym in symbols_map if sym not in unrelevent_symbols]
        if symbol_type=='int':
            for entity_id in self._entities_map:
                self._entities_map[entity_id]=sorted([sym_ti for sym_ti in self._entities_map[entity_id] if sym_ti._symbol not in unrelevent_symbols],
                                                     key=self.sort_str_int)
        else:
            for entity_id in self._entities_map:
                self._entities_map[entity_id]=sorted([sym_ti for sym_ti in self._entities_map[entity_id] if sym_ti._symbol not in unrelevent_symbols],
                                                     key=operator.attrgetter('_start_time', '_end_time','_symbol'))

    def parse_kml_input(self,file_path,num_comma,symbol_type):
        self.parse_temporal_var_dict(file_path)
        self.parse_file_into_symbolic_time_intervals_parts(file_path, self._symbolic_interval_start_point,symbol_type,num_comma)


    def build_karma_index(self, skip_followers, num_of_bins):

        """
        build the 2 symbols index , the index is build of map of maps.
        :param skip_followers: bool,decide if to skip 2 followers symbols (from the same temporal variable)
        :param num_of_bins: integer ,the number of bins that was used for the temporal abstraction process
        :return:
        """

        for entity in self._entities_map.keys():
            time_intervals = self._entities_map[entity]
            time_intervals_length = len(time_intervals)

            self._logger.debug('handling entity %s with %s intervals.', str(entity), str(time_intervals_length))

            # since the intervals are sorted by start time, avoid making n^2 checks.
            for sym_ti1_index in range(0, time_intervals_length - 1):
                for sym_ti2_index in range(sym_ti1_index+1, time_intervals_length):
                    sym_ti1 = time_intervals[sym_ti1_index]
                    sym_ti2 = time_intervals[sym_ti2_index]

                    s2_minus_e1 = sym_ti2._start_time - sym_ti1._end_time

                    # max gap reached, no need to proceed with the check.
                    if s2_minus_e1 > self._max_gap:
                        break

                    if sym_ti1._symbol == sym_ti2._symbol:
                        continue

                    #TODO need to implement the temporal variables dictionary
                    if skip_followers == True and abs(int(sym_ti1._symbol)-int(sym_ti2._symbol)) == 1:
                        #if math.floor(sym_ti1._symbol/num_of_bins) == math.floor(sym_ti2._symbol/num_of_bins) or (max(sym_ti1._symbol,sym_ti2._symbol) % num_of_bins) == 0:
                        if self._var_to_symbols[str(sym_ti1._symbol)]==self._var_to_symbols[str(sym_ti2._symbol)]:
                            continue
                    relation = self._relation_handler_obj.check_relation(sym_ti1, sym_ti2, self._epsilon, self._max_gap);
                    symbols_key = (sym_ti1._symbol, sym_ti2._symbol)
                    if relation != RelationHandler.RELATION_NOT_DEFINED:

                        if relation==6 : #check if the opposite key for equal already exist
                            opposite_key=(sym_ti2._symbol, sym_ti1._symbol)
                            if opposite_key in self._dharma_index.keys() and relation in self._dharma_index[opposite_key].keys() :
                                continue
                        if symbols_key not in  self._dharma_index.keys():
                            self._dharma_index[symbols_key] = {relation:{entity:[[sym_ti1, sym_ti2]]}}

                        elif relation not in self._dharma_index[symbols_key].keys():
                            self._dharma_index[symbols_key].update({relation: {entity: [[sym_ti1, sym_ti2]]}})

                        elif entity not in self._dharma_index[symbols_key][relation].keys():
                            self._dharma_index[symbols_key][relation].update({entity: [[sym_ti1, sym_ti2]]})

                        else:
                            self._dharma_index[symbols_key][relation][entity].append([sym_ti1, sym_ti2])
                    else:
                        continue

    def trim_karma_index_base_on_support(self,min_vertical_support_for_trim):

        """
        Trim the index for the symbols and relations that dont have minimum support.
        remove symbols from _frequent_symbols that were deleted from the index
        """

        for two_symbols, relation in self._dharma_index.items():
            self._dharma_index[two_symbols]={relation: entities for relation,entities in self._dharma_index[two_symbols].items() if len(entities)>=len(self._entities_map)*min_vertical_support_for_trim}
        self._dharma_index={key:value for key,value in self._dharma_index.items() if value}
        self._frequent_symbols=list(set(list(chain(*self._dharma_index.keys()))))

    def get_frequent_symbol_pairs(self):
        """
        Return all the current key pairs in dharma index.
        after fit they should be the frequent key pairs.
        :return: current key pairs in dharma index.
        """
        return self._dharma_index.keys()

    def get_relations_for_two_symbols(self, symbol_a, symbol_b):
        """
        return a list of relations for the input key in _dharma_index
        :param symbol_a: int, first key symbol
        :param symbol_b: int, second key symbol
        :return: list of relations
        """

        relations = []

        symbols_key = (symbol_a, symbol_b)
        if symbols_key in self._dharma_index.keys():
            relations=list(self._dharma_index[symbols_key].keys())

        return relations

    def get_all_pairs_mapped_by_entity_id(self, symbol_a, symbol_b, relation):

        """
        Get a mapping of entity id and array of STI pairs that have the given symbols and relation between them.

        Returned Mapping of STI pairs constraint:

        the first symbol in pair should correspond to symbol_a
        the second symbol in pair should correspond to symbol_b

        given relation must exist between symbol_a and symbol_b

        if constrains not meet - return empty array.

        :param symbol_a: the first symbol
        :param symbol_b: the second symbol
        :param relation: that is between symbol_a and symbol_b
        :return: List of STI pairs as defined by the constrains.
        """
        mapping = {}

        symbols_key = (symbol_a, symbol_b)

        if symbols_key not in self._dharma_index.keys():
            return mapping

        if relation not in self._dharma_index[symbols_key].keys():
            return mapping

        for entity_id in self._dharma_index[symbols_key][relation].keys():
            mapping[entity_id] = []
            for sti_pair in self._dharma_index[symbols_key][relation][entity_id]:
                mapping[entity_id].append(sti_pair)

        return mapping

    def get_pairs(self, symbol_a, symbol_b, relation, entity_id, sym_ti):
        """

        return a list of symbolic time interval pairs that the first symbolic time intervals
        corresponds to the given one, and to other arguments.

        for example:

        if given A, B , r , 22, STI

        Retrun all the pairs from entity with id 22 that corisonds to A r B and the first STI in each pair equals
        the given one.

        :param symbol_a: first symbol
        :param symbol_b: second symbol
        :param relation: relation between symbol_a and symbol_b
        :param entity_id: entity id when the given STI contained.
        :param sym_ti: symbolic time interval.
        :return: list of STI pairs matching the method logic.
        """
        pairs = []

        symbols_key = (symbol_a, symbol_b)

        if symbols_key not in self._dharma_index.keys():
            return pairs

        if relation not in self._dharma_index[symbols_key].keys():
            return pairs

        if entity_id not in self._dharma_index[symbols_key][relation].keys():
            return pairs

        for pair in self._dharma_index[symbols_key][relation][entity_id]:
            if pair[0] == sym_ti:
                pairs.append(pair)

        return pairs


    def is_pair_exist(self, relation, entity_id, sym_ti_a, sym_ti_b):
        """

        check if a given STI pair exist for Symbol A and SymbolB relation in a entity
        corresponding to the given entity id.

        :param symbol_a: first symbol
        :param symbol_b: second symbol
        :param relation: relation between first symbol and second symbol
        :param entity_id: the entity id that need to be checked if contains the given STIs.
        :param sym_ti_a: first symbolic interval
        :param sym_ti_b: second symbolic interval
        :return: true if found, false otherwise
        """

        symbols_key = (sym_ti_a._symbol, sym_ti_b._symbol)

        if symbols_key not in self._dharma_index.keys():
            return False

        if relation not in self._dharma_index[symbols_key].keys():
            return False

        if entity_id not in self._dharma_index[symbols_key][relation].keys():
            return False

        for pair in self._dharma_index[symbols_key][relation][entity_id]:
            if pair[0] == sym_ti_a and pair[1] == sym_ti_b:
                return True

        return False


    def get_relevent_entries_in_index_by_last_symbol(self,last_symbol):
        """

        :param last_symbol: int, the lst symbol in the current tirp
        :return: dictionary of relevant keys
        """
        relevent_entries={(key1,key2):value for (key1,key2),value in self._dharma_index.items() if key1==last_symbol}
        return relevent_entries
