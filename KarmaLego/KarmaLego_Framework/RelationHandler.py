from copy import copy


class AllenSevenRelationEngine(object):
    """
        Engine to handle all 7 Allen`s relations.

        the order of the relations is critical for transitivity table creation, do not change!!!

        implementation based on:
        https://www.ics.uci.edu/~alspaugh/cls/shr/allen.html
    """

    NOT_DEFINED_DESCRIPTION = 'NOT DEFINED';
    NOT_DEFINED = -1;
    BEFORE = 0;
    MEET = 1;
    OVERLAP = 2;
    FINISHBY = 3;
    CONTAIN = 4;
    STARTS = 5;
    EQUAL = 6;

    RELATION_CHARS = ['p','m','o','F','D','s','e'];
    RELATION_CHARS_FRESKA = ['<','m','o','f','c','s','='];
    RELATION_FULL_DESCRIPTION = ['BEFORE','MEETS','OVERLAPS','FINISH-BY','CONTAINS','STARTS','EQUALS'];

    def __init__(self):

        """
        Construct the 7 allen relations transitivity table.

        """
        self._transitivity_table = {};

        # init the table to hold empty  arrays.
        for i in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.EQUAL + 1):
            self._transitivity_table[i] ={};
            for j in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.EQUAL + 1):
                self._transitivity_table[i][j] = [];

        # handle BEFORE relation row
        row = AllenSevenRelationEngine.BEFORE;

        for column in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.EQUAL + 1):
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.BEFORE);

        # handle MEET relation row
        row = AllenSevenRelationEngine.MEET;

        for column in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.CONTAIN + 1):
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.BEFORE);

        for column in range(AllenSevenRelationEngine.STARTS, AllenSevenRelationEngine.EQUAL + 1):
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.MEET);

        # handle OVERLAP relation row
        row = AllenSevenRelationEngine.OVERLAP;

        for column in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.MEET + 1):
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.BEFORE);

        for column in range(AllenSevenRelationEngine.STARTS, AllenSevenRelationEngine.EQUAL + 1):
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.OVERLAP);

        for column in range(AllenSevenRelationEngine.OVERLAP, AllenSevenRelationEngine.FINISHBY + 1):
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.BEFORE);
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.MEET);
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.OVERLAP);

        for relation in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.CONTAIN + 1):
            self._transitivity_table[row][AllenSevenRelationEngine.CONTAIN].append(relation);

        # handle FINISHBY relation row
        row = AllenSevenRelationEngine.FINISHBY;

        for column in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.CONTAIN + 1):
            self._transitivity_table[row][column].append(column);

        self._transitivity_table[row][AllenSevenRelationEngine.STARTS].append(AllenSevenRelationEngine.OVERLAP);
        self._transitivity_table[row][AllenSevenRelationEngine.EQUAL].append(AllenSevenRelationEngine.FINISHBY);

        # handle CONTAIN relation row
        row = AllenSevenRelationEngine.CONTAIN;

        for relation in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.CONTAIN + 1):
            self._transitivity_table[row][AllenSevenRelationEngine.BEFORE].append(relation);

        for relation in range(AllenSevenRelationEngine.OVERLAP, AllenSevenRelationEngine.CONTAIN + 1):
            self._transitivity_table[row][AllenSevenRelationEngine.MEET].append(relation);
            self._transitivity_table[row][AllenSevenRelationEngine.OVERLAP].append(relation);
            self._transitivity_table[row][AllenSevenRelationEngine.STARTS].append(relation);

        self._transitivity_table[row][AllenSevenRelationEngine.FINISHBY].append(AllenSevenRelationEngine.CONTAIN);
        self._transitivity_table[row][AllenSevenRelationEngine.CONTAIN].append(AllenSevenRelationEngine.CONTAIN);
        self._transitivity_table[row][AllenSevenRelationEngine.EQUAL].append(AllenSevenRelationEngine.CONTAIN);

        # handle STARTS relation row
        row = AllenSevenRelationEngine.STARTS;

        for column in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.MEET + 1):
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.BEFORE);

        for column in range(AllenSevenRelationEngine.STARTS, AllenSevenRelationEngine.EQUAL + 1):
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.STARTS);

        for column in range(AllenSevenRelationEngine.OVERLAP, AllenSevenRelationEngine.FINISHBY + 1):
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.BEFORE);
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.MEET);
            self._transitivity_table[row][column].append(AllenSevenRelationEngine.OVERLAP);

        for relation in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.CONTAIN + 1):
            self._transitivity_table[row][AllenSevenRelationEngine.CONTAIN].append(relation);

        # handle EQUAL relation row
        row = AllenSevenRelationEngine.EQUAL;

        for column in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.EQUAL + 1):
            self._transitivity_table[row][column].append(column);

    def print_transitivity_table(self):
        st = '';
        for i in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.EQUAL + 1):
            st = '';
            for j in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.EQUAL + 1):
                st += str([self.get_short_description(rel) for rel in self._transitivity_table[i][j]])+'  ';
            print(st);


    def get_transitivity_list(self, relation_ab, relation_bc):
        """
             return a List of transitive relations to the given ones.
               :param relation_ab: relation between two symbols AB.
               :param relation_bc: relation between two symbols BC.
               :return: list of possible relations between two symbols AC.

        """
        return copy(self._transitivity_table[relation_ab][relation_bc]);

    def check_relation(self, sym_ti1, sym_ti2, epsilon, max_gap):
        """
                check the relation between two symbolic time intervals
                :param sym_ti1:SymbolicTimeInterval, first object
                :param sym_ti2: SymbolicTimeInterval, second object
                :param epsilon: int, minimum time difference between two intervals that defines the relation
                :param max_gap: int,  maximum time difference between two time intervals for indexing to TIRP
                :return: the number of relation
                """
        relation = AllenSevenRelationEngine.NOT_DEFINED;

        if sym_ti1._start_time > sym_ti2._start_time:
            return relation

        e1_minus_s2 = sym_ti1._end_time - sym_ti2._start_time;
        s2_minus_s1 = sym_ti2._start_time - sym_ti1._start_time;
        e1_minus_e2 = sym_ti1._end_time - sym_ti2._end_time;
        e2_minus_e1 = sym_ti2._end_time - sym_ti1._end_time;
        s2_minus_e1 = sym_ti2._start_time - sym_ti1._end_time;

        if s2_minus_e1 > max_gap:
            return relation

        if s2_minus_e1 > epsilon and s2_minus_e1 < max_gap:
            relation = AllenSevenRelationEngine.BEFORE

        elif s2_minus_s1 > epsilon and abs(e1_minus_e2) <= epsilon:
            relation = AllenSevenRelationEngine.FINISHBY

        elif s2_minus_s1 > epsilon and abs(e1_minus_s2) <= epsilon and e1_minus_e2 < epsilon:
            relation = AllenSevenRelationEngine.MEET

        elif s2_minus_s1 > epsilon and e1_minus_s2 > epsilon and e1_minus_e2 < epsilon:
            relation = AllenSevenRelationEngine.OVERLAP

        elif abs(s2_minus_s1) <= epsilon and e2_minus_e1 > epsilon:
            relation = AllenSevenRelationEngine.STARTS

        elif s2_minus_s1 > epsilon and e1_minus_e2 > epsilon:
            relation = AllenSevenRelationEngine.CONTAIN

        elif abs(s2_minus_s1) <= epsilon and abs(e1_minus_e2) <= epsilon:
            relation = AllenSevenRelationEngine.EQUAL

        return relation;

    def get_full_description(self, relation):
        if relation == AllenSevenRelationEngine.NOT_DEFINED:
            return AllenSevenRelationEngine.NOT_DEFINED_DESCRIPTION;
        return AllenSevenRelationEngine.RELATION_FULL_DESCRIPTION[relation];

    def get_short_description(self, relation):
        if relation == AllenSevenRelationEngine.NOT_DEFINED:
            return AllenSevenRelationEngine.NOT_DEFINED_DESCRIPTION;
        return AllenSevenRelationEngine.RELATION_CHARS_FRESKA[relation];


class KLRelationEngine(object):

    #TODO - get full description for this engine.
    """
        Engine to handle all KL relations logic.
    """
    NOT_DEFINED = -1;
    BEFORE = 0;
    OVERLAP = 1;
    CONTAIN = 2;

    def __init__(self):
        self._relation_map_kl = {'NOT_DEFINED': KLRelationEngine.NOT_DEFINED,
                                 'BEFORE': 0,
                                 'OVERLAP': 1,
                                 'CONTAIN': 2}

    def check_relation(self,sym_ti1,sym_ti2,epsilon,max_gap):
        """


        check the relation between two symbolic time intervals.
        :param sym_ti1:SymbolicTimeInterval, first object
        :param sym_ti2: SymbolicTimeInterval, second object
        :param epsilon: int, minimum time difference between two intervals that defines the relation
        :param max_gap: int,  maximum time difference between two time intervals for indexing to TIRP
        :return: the number of relation
        """
        relation = KLRelationEngine.RELATION_NOT_DEFINED;

        if relation == self._relation_map_allen['BEFORE'] or self._relation_map_allen['MEET']:
            relation = self._relation_map_kl['BEFORE']

        elif relation ==self._relation_map_allen['OVERLAP']:
            relation = self._relation_map_kl['OVERLAP']
        else:
            relation = self._relation_map_kl['CONTAIN']

        return relation

    def get_transitivity_list(self, relation_ab, relation_bc):
        print("NOT IMPLEMENTED YET");
        return None;

    def get_full_description(self, relation):
        print("NOT IMPLEMENTED YET");
        return None;

    def get_short_description(self, relation):
        print("NOT IMPLEMENTED YET");
        return None;



class RelationHandler(object):
    RELATION_NOT_DEFINED = -1;
    RELATION_KL = 3;
    RELATION_ALLEN_7 = 7;

    def __init__(self, num_of_relations):

        self._num_of_relations = num_of_relations;

        self._relations_handler_engine = None;

        # set the current engine based on the given relations number.
        if self._num_of_relations == RelationHandler.RELATION_ALLEN_7:
            self._relations_handler_engine = AllenSevenRelationEngine();

        elif self._num_of_relations == RelationHandler.RELATION_KL:
            self._relations_handler_engine = KLRelationEngine();


    def check_relation(self,sym_ti1,sym_ti2,epsilon,max_gap):
        """
            check the relation between two symbolic time intervals using the current relation engine.
            :param sym_ti1:SymbolicTimeInterval, first object
            :param sym_ti2: SymbolicTimeInterval, second object
            :param epsilon: int, minimum time difference between two intervals that defines the relation
            :param max_gap: int,  maximum time difference between two time intervals for indexing to TIRP
            :return: the number of relation
        """
        return self._relations_handler_engine.check_relation(sym_ti1,sym_ti2,epsilon,max_gap);

    def get_transitivity_list(self, relation_ab, relation_bc):
        """
           return a List of transitive relations to the given relations from the current engine.
           :param relation_ab: relation between two symbols AB.
           :param relation_bc: relation between two symbols BC.
           :return: list of possible relations between two symbols AC.
        """
        return self._relations_handler_engine.get_transitivity_list(relation_ab, relation_bc);

    def get_full_description(self, relation):
        """
            Get full name of a given relation from the current engine.
            :param relation: numeric representation of a relation
            :return: full name of a given relation
        """
        return self._relations_handler_engine.get_full_description(relation);

    def get_short_description(self, relation):
        """
            Get short name/char of a given relation from the current engine.
            :param relation: numeric representation of a relation
            :return: short name/char of a given relation
        """
        return self._relations_handler_engine.get_short_description(relation);