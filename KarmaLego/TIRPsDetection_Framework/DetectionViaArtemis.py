from KarmaLego.KarmaLego_Framework.RelationHandler import RelationHandler
import os
import logging
from KarmaLego.KarmaLego_Framework.SymbolicTimeInterval import SymbolicTimeInterval
import more_itertools
from operator import itemgetter
import itertools
import threading


FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('KarmaTests')
logger.setLevel(20)

class DetectionViaArtemis(object):

    def __init__(self,num_relations=7):
        self._relation_handler_obj = RelationHandler(num_relations)
        self._entities_map_to_detect={}


    def Sequential_TIRPs_Detection_multiply_entities(self, frequent_tirps,time_intervals_entities_path,similarity_limit,detection_type,max_gap,epsilon=0,num_comma=2):
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
        tirps_detected=[]
        self.parse_temporal_var_dict(time_intervals_entities_path)
        self.parse_file_into_symbolic_time_intervals(time_intervals_entities_path,num_comma, self._symbolic_interval_start_point)
        if detection_type=='SW':
            tirps_detected=self.Artemis_Sliding_Window_Detection(frequent_tirps, similarity_limit, epsilon, max_gap)
        elif detection_type=='AC':
            tirps_detected = self.Artemis_All_Combinations_Detection(frequent_tirps, similarity_limit, epsilon, max_gap)
        elif detection_type=='SDA':
            tirps_detected = self.Sequential_TIRPs_Detection_with_Artemis(frequent_tirps, epsilon,max_gap,similarity_limit)
        elif detection_type=='AC2':
            tirps_detected=[]
            jobs = []
            maxthreads = 8
            sema = threading.Semaphore(value=maxthreads)
            for tirp in frequent_tirps:
                p = threading.Thread(target=self.Artemis_All_Combinations_Detection_parallel, args=(tirp,tirps_detected,similarity_limit, epsilon,max_gap))
                jobs.append(p)

            # start run statistics in parallel
            for j in jobs:
                j.start()

            for j in jobs:
                j.join()
        return tirps_detected


    def Artemis_Sliding_Window_Detection(self, frequent_tirps, similarity_limit, epsilon, max_gap):
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
            tirpSearched._Artemis_by_entity = {}
            tirp_length=len(tirp._symbols)
            tirp_map_list_before, tirp_map_list_after=self.mapping_step_for_TIRP(tirp)
            for entity_id in self._entities_map_to_detect:
                first_detection=False
                time_intervals_e=self._entities_map_to_detect[entity_id]
                entity_sliding_window_index_list=list(more_itertools.windowed(range(0,len(time_intervals_e)), n=tirp_length, step=1))
                for sliding_window in entity_sliding_window_index_list:
                    gap_validation=True
                    record_pattern =itemgetter(*sliding_window)(time_intervals_e)
                    for i in range(1,len(record_pattern)):
                        if (record_pattern[i]._start_time - record_pattern[i-1]._end_time) >= max_gap:
                            gap_validation=False
                    if gap_validation==True:
                        entity_map_list_before, entity_map_list_after = self.mapping_step_for_symbolic_time_intervals(record_pattern)
                        Artemis=self.Artemis(tirp_map_list_before, tirp_map_list_after, entity_map_list_before,entity_map_list_after)
                        if Artemis>similarity_limit:
                            if first_detection == False:
                                tirpSearched._supporting_sequences_by_entity[entity_id] = []
                                tirpSearched._Artemis_by_entity[entity_id] = []
                                first_detection = True
                            tirpSearched._supporting_sequences_by_entity[entity_id].append(record_pattern)
                            tirpSearched._Artemis_by_entity[entity_id].append(Artemis)
                            found = True
            if found==True:
                tirps_detected.append(tirpSearched)
        return tirps_detected

    def Artemis_All_Combinations_Detection(self,frequent_tirps,similarity_limit, epsilon,max_gap):
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
            tirpSearched._Artemis_by_entity = {}
            tirp_length=len(tirp._symbols)
            tirp_map_list_before, tirp_map_list_after=self.mapping_step_for_TIRP(tirp)
            for entity_id in self._entities_map_to_detect:
                first_detection=False
                time_intervals_e=self._entities_map_to_detect[entity_id]
                for comb in itertools.combinations(list(range(0,len(time_intervals_e))),tirp_length):
                    gap_validation=True
                    record_pattern =itemgetter(*comb)(time_intervals_e)
                    for i in  range(0,tirp_length-1):
                        if (record_pattern[tirp_length-1]._start_time - record_pattern[i]._end_time) >= max_gap:
                            gap_validation=False
                    if gap_validation==True:
                        entity_map_list_before, entity_map_list_after = self.mapping_step_for_symbolic_time_intervals(record_pattern)
                        Artemis=self.Artemis(tirp_map_list_before, tirp_map_list_after, entity_map_list_before,entity_map_list_after)
                        if Artemis>similarity_limit:
                            if first_detection == False:
                                tirpSearched._supporting_sequences_by_entity[entity_id] = []
                                tirpSearched._Artemis_by_entity[entity_id]=[]
                                first_detection = True
                            tirpSearched._supporting_sequences_by_entity[entity_id].append(record_pattern)
                            found = True
                            tirpSearched._Artemis_by_entity[entity_id].append(Artemis)
            if found==True:
                tirps_detected.append(tirpSearched)
        return tirps_detected



    def Artemis_All_Combinations_Detection_parallel(self,tirp,tirps_detected,similarity_limit, epsilon,max_gap):
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
        found=False
        tirpSearched=tirp.copy()
        tirpSearched._supporting_sequences_by_entity = {}
        tirpSearched._Artemis_by_entity = {}
        tirp_length=len(tirp._symbols)
        tirp_map_list_before, tirp_map_list_after=self.mapping_step_for_TIRP(tirp)
        for entity_id in self._entities_map_to_detect:
            first_detection=False
            time_intervals_e=self._entities_map_to_detect[entity_id]
            for comb in itertools.combinations(list(range(0,len(time_intervals_e))),tirp_length):
                gap_validation=True
                record_pattern =itemgetter(*comb)(time_intervals_e)
                for i in  range(0,tirp_length-1):
                    if (record_pattern[tirp_length-1]._start_time - record_pattern[i]._end_time) >= max_gap:
                        gap_validation=False
                if gap_validation==True:
                    entity_map_list_before, entity_map_list_after = self.mapping_step_for_symbolic_time_intervals(record_pattern)
                    Artemis=self.Artemis(tirp_map_list_before, tirp_map_list_after, entity_map_list_before,entity_map_list_after)
                    if Artemis>similarity_limit:
                        if first_detection == False:
                            tirpSearched._supporting_sequences_by_entity[entity_id] = []
                            tirpSearched._Artemis_by_entity[entity_id]=[]
                            first_detection = True
                        tirpSearched._supporting_sequences_by_entity[entity_id].append(record_pattern)
                        found = True
                        print(Artemis)
                        tirpSearched._Artemis_by_entity[entity_id].append(Artemis)
        if found==True:
            tirps_detected.append(tirpSearched)


    def Sequential_TIRPs_Detection_with_Artemis(self,frequent_tirps, epsilon,max_gap,similarity_limit):
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
            tirp_length = len(tirp._symbols)
            tirp_map_list_before, tirp_map_list_after = self.mapping_step_for_TIRP(tirp)
            found=False
            tirpSearched=tirp.copy()
            tirpSearched._supporting_sequences_by_entity = {}
            tirpSearched._Artemis_by_entity = {}
            for entity_id in self._entities_map_to_detect:
                first_detection = True
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
                                gap_validation = True
                                if (len(inst1)>=1):
                                    for i in range(len(inst1)): #need to fix to (0,len(inst1)-1)
                                        if (time_intervals_e[fi]._start_time-inst1[len(inst1)-1-i]._end_time) >= max_gap:##NEED TO fix: the validation is between the interval that was added and all the others: inst1[len(inst1)]._start_time - inst1[i]._end_time
                                            gap_validation = False
                                if gap_validation == True:
                                    inst2=[]
                                    for sym_ti in inst1:
                                        sym_ti_to_add=sym_ti.copy()
                                        inst2.append(sym_ti_to_add)
                                    inst2.append(time_intervals_e[fi])
                                    new_insts.append(inst2)
                        inst = new_insts
                if len(inst) >0:
                    for time_intervals_e in inst:
                        entity_map_list_before, entity_map_list_after = self.mapping_step_for_symbolic_time_intervals(time_intervals_e)
                        Artemis = self.Artemis(tirp_map_list_before, tirp_map_list_after, entity_map_list_before, entity_map_list_after)
                        if Artemis > similarity_limit:
                            if first_detection == True:
                                tirpSearched._supporting_sequences_by_entity[entity_id] = []
                                tirpSearched._Artemis_by_entity[entity_id] = []
                                first_detection = False
                            tirpSearched._supporting_sequences_by_entity[entity_id].append(time_intervals_e)
                            tirpSearched._Artemis_by_entity[entity_id].append(Artemis)
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





    ##############################################################
    def Artemis(self, tirp_map_list_before,tirp_map_list_after, entity_map_list_before,entity_map_list_after):
        """
        calcilate the similarity in percentage between TIRP and pattern
        :param tirp_map_list_before:
        :param tirp_map_list_after:
        :param entity_map_list_before:
        :param entity_map_list_after:
        :return:
        """
        length_tirp=len(tirp_map_list_before)
        numerator=length_tirp*length_tirp
        for i,lSi in  enumerate(tirp_map_list_before):
            for j,LRSi in  enumerate(lSi):
                if LRSi==entity_map_list_before[i][j]:
                    numerator=numerator-1
        for i,rSi in  enumerate(tirp_map_list_after):
            for j,LRSi in  enumerate(rSi):
                if LRSi==entity_map_list_after[i][j]:
                    numerator=numerator-1
        distance=numerator/(length_tirp*length_tirp)
        similarity=1-distance
        return similarity


    def mapping_step_for_TIRP(self, tirp):
        extra_symbol = '@'
        tirp_map_list_before=[]
        tirp_map_list_after = []
        for i,symbol in enumerate(tirp._symbols):
            tirp_map_list_before.append([])
            tirp_map_list_after.append([])
            tirp_map_list_before[i].append([extra_symbol,0,symbol])
            for before in range(i):
                relation=tirp._tirp_matrix.get_relation(before,i)
                tirp_map_list_before[i].append([tirp._symbols[before], relation, symbol])
            for after in range(i+1,len(tirp._symbols)):
                relation = tirp._tirp_matrix.get_relation(i, after)
                tirp_map_list_after[i].append([symbol, relation, tirp._symbols[after]])
        return tirp_map_list_before,tirp_map_list_after


    def mapping_step_for_symbolic_time_intervals(self, time_intervals_e):
        extra_symbol = '@'
        entity_map_list_before = []
        entity_map_list_after = []
        for i, sym_ti in enumerate(time_intervals_e):
            entity_map_list_before.append([])
            entity_map_list_after.append([])
            entity_map_list_before[i].append([extra_symbol, 0, sym_ti._symbol])
            for before in range(i):
                relation=self._relation_handler_obj.check_relation(time_intervals_e[before], time_intervals_e[i],epsilon=0, max_gap=50)
                entity_map_list_before[i].append([time_intervals_e[before]._symbol, relation, sym_ti._symbol])
            for after in range(i + 1, len(time_intervals_e)):
                relation = self._relation_handler_obj.check_relation(time_intervals_e[i],time_intervals_e[after],epsilon=0, max_gap=50)
                entity_map_list_after[i].append([ sym_ti._symbol, relation, time_intervals_e[after]._symbol])
        return entity_map_list_before,entity_map_list_after



