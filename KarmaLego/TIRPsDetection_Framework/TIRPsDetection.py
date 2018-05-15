from KarmaLego.KarmaLego_Framework.RelationHandler import RelationHandler
import os
import logging
from KarmaLego.KarmaLego_Framework.SymbolicTimeInterval import SymbolicTimeInterval

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('KarmaTests')
logger.setLevel(20)

class TIRPsDetection(object):

    def __init__(self,num_relations=7):
        self._relation_handler_obj = RelationHandler(num_relations)
        self._entities_map_to_detect={}


    def Sequential_TIRPs_Detection_multiply_entities(self, frequent_tirps,time_intervals_entities_path, epsilon=0,max_gap=50,num_comma=2):
        """
        Given a path to a file containing symbolic time intervals by instances, the function will call to the function
        parse_file_into_symbolic_time_intervals in order to parse that file into _entities_map_to_detect, then the function
        will call to the function Sequential_TIRPs_Detection in order to search all the TIRPs detected by Lego at the instances
        :param time_intervals_entities_path: string, the path to the symbolic time intervals file
        :param tirps_detected_path:  string, the path to the detected TIRPs
        :param epsilon: int, minimum time difference between two intervals that defines the relation
        :param max_gap: int,  maximum time difference between two time intervals for indexing to TIRP
         :param frequent_tirps: list of TIRPs -the frequwnt tirps to detect
        :return: tirps_detected: TIRP, the detected TIRP
        """
        self.parse_temporal_var_dict(time_intervals_entities_path)
        self.parse_file_into_symbolic_time_intervals(time_intervals_entities_path,num_comma, self._symbolic_interval_start_point)
        tirps_detected=self.Sequential_TIRPs_Detection(frequent_tirps,epsilon,max_gap)
        return tirps_detected


    def Sequential_TIRPs_Detection(self,frequent_tirps, epsilon,max_gap):
        """
        The algorithm detects all of the instances for each of the TIRPs. For each TIRP, it starts by going
        over all of the symbolic time intervals. If the first symbol of the current TIRP (tirp.s[0]) was detected,
        a while loop starts to look for the TIRP's next symbols, and verifies that their temporal relations
        with the previous detected symbolic time intervals are the same as in the TIRP temporal relations definition
        If the time duration between the i-interval and the j-interval is larger than max_gap, the search for instances
        is stopped.
        :param frequent_tirps: list of TIRPs -the frequwnt tirps to detect
        :param epsilon: int, minimum time difference between two intervals that defines the relation
        :param max_gap: int,  maximum time difference between two time intervals for indexing to TIRP
        """
        tirps_detected = []
        for tirp in frequent_tirps:
            found=False
            tirpSearched=tirp.copy()
            tirpSearched._supporting_sequences_by_entity = {}
            first_detection = False
            for entity_id in self._entities_map_to_detect:
                time_intervals_e=self._entities_map_to_detect[entity_id]
                inst=[]
                for tIdx,valTIRP in enumerate(tirp._symbols):
                    if tIdx==0:
                        for idx, sym_ti in enumerate(time_intervals_e):
                            if sym_ti._symbol == valTIRP:
                                inst1=[]
                                inst1.append(sym_ti)
                                inst.append(inst1)
                    else:
                        found_location=[]
                        for idx,sym_ti in enumerate(time_intervals_e):
                             if sym_ti._symbol==valTIRP:
                                found_location.append(idx)
                        new_insts=[]
                        for fi in found_location:
                            for inst1 in inst:
                                relationEquel = True
                                for r in range(len(inst1)):
                                    if tirpSearched._tirp_matrix.get_relation(tIdx - r - 1,tIdx) != self._relation_handler_obj.check_relation(
                                            inst1[len(inst1) - r - 1], time_intervals_e[fi], epsilon, max_gap):
                                        relationEquel = False
                                if relationEquel == True:
                                    inst2=[]
                                    for sym_ti in inst1:
                                        sym_ti_to_add=sym_ti.copy()
                                        inst2.append(sym_ti_to_add)
                                    inst2.append(time_intervals_e[fi])
                                    new_insts.append(inst2)
                        inst = new_insts
                if len(inst) >0:
                    tirpSearched._supporting_sequences_by_entity[entity_id] = []
                    for inst1 in inst:
                        tirpSearched._supporting_sequences_by_entity[entity_id].append(inst1)
                    found = True
            if found==True:
                tirps_detected.append(tirpSearched)
        return tirps_detected

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

        return new_tirp

    def print_detected_tirps(self,path,detected_tirps):
        """
        printing all the frequent TIRPs into a file
        :param path: the output path to print the TIRP
        :param detected_tirps: list (TIRPs) to detect
        :return: None - a file with the TIRPs
        """
        try:
            os.remove(path)
        except OSError:
            pass
        for tirp in detected_tirps:
            tirp.print_tirp(path,self._relation_handler_obj._num_of_relations)

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

    def parse_file_into_symbolic_time_intervals(self, file_path,num_comma, start_index=0):
        """
        parse the file to a map of entities to detect with their symbolic time intervals
        sort the symbolic time intervals in a lexicographic order
        :param file_path: string, the path to the symbolic time intervals file
        :param start_index: int, the row fro mwhich to parse the symbolic time intervals
        :return: nothing
        """
        self._entities_map_to_detect = {}
        with open(file_path) as f:
            lines = f.readlines()[start_index:]
        for i in range(0,len(lines),2):
            entity_id=int(lines[i].replace(";",""))
            sym_ti_ls = lines[i+1].split(";")
            for sym_ti in sym_ti_ls[:-1]:
                parts=sym_ti.split(",")
                st=int(parts[0])
                et=int(parts[1])
                symbol = parts[num_comma]
                sym_ti_obj=SymbolicTimeInterval(start_time=st, end_time=et, symbol=symbol)
                if entity_id not in self._entities_map_to_detect:
                    self._entities_map_to_detect[entity_id]=[sym_ti_obj]
                else:
                    self._entities_map_to_detect[entity_id].append(sym_ti_obj)

