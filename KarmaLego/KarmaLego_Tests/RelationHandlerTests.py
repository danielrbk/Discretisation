from KarmaLego.KarmaLego_Framework.RelationHandler import *
from KarmaLego.KarmaLego_Framework.SymbolicTimeInterval import SymbolicTimeInterval

import logging

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('RelationHandlerTester')
logger.setLevel(20)

def checkRelation(handler, sti1, sti2, epsilon, maxGap, relation):
    if handler.check_relation(sti1, sti2, epsilon, maxGap) != relation:
        logger.error('[FAILED] '+handler.get_full_description(relation));
    else:
        logger.info('[PASSED] '+handler.get_full_description(relation))


def checkNotInGap(epsilon, maxGap):
    rh = RelationHandler(RelationHandler.RELATION_ALLEN_7);

    logger.debug('Testing Not in gap, epsilon: '+str(epsilon)+', max gap: '+str(maxGap))

    sti1 = SymbolicTimeInterval(1, 3, 'A', 345);

    sti2 = SymbolicTimeInterval(3 + maxGap + 1, 3 + maxGap + 8, 'B', 567);

    checkRelation(rh, sti1, sti2, epsilon, maxGap, AllenSevenRelationEngine.NOT_DEFINED);


def checkRealtion7Before(epsilon, maxGap):

    rh = RelationHandler(RelationHandler.RELATION_ALLEN_7);

    logger.debug('Testing BEFORE in 7 relations, epsilon: ' + str(epsilon) + ', max gap: ' + str(maxGap))

    sti1 = SymbolicTimeInterval(1, 3, 'A', 345);
    sti2 = SymbolicTimeInterval(4, 6, 'B', 567);

    checkRelation(rh, sti1, sti2, epsilon, maxGap, AllenSevenRelationEngine.BEFORE);

def checkRealtion7Meets(epsilon, maxGap):

    rh = RelationHandler(RelationHandler.RELATION_ALLEN_7);

    logger.debug('Testing MEETS in 7 relations, epsilon: ' + str(epsilon) + ', max gap: ' + str(maxGap))

    sti1 = SymbolicTimeInterval(1, 3, 'A', 345);
    sti2 = SymbolicTimeInterval(3, 6, 'B', 567);

    checkRelation(rh, sti1, sti2, epsilon, maxGap, AllenSevenRelationEngine.MEET);

def checkRealtion7Overlaps(epsilon, maxGap):

    rh = RelationHandler(RelationHandler.RELATION_ALLEN_7);

    logger.debug('Testing OVERLAPS in 7 relations, epsilon: ' + str(epsilon) + ', max gap: ' + str(maxGap))

    sti1 = SymbolicTimeInterval(1, 3, 'A', 345);
    sti2 = SymbolicTimeInterval(2, 6, 'B', 567);

    checkRelation(rh, sti1, sti2, epsilon, maxGap, AllenSevenRelationEngine.OVERLAP);

def checkRealtion7Contains(epsilon, maxGap):

    rh = RelationHandler(RelationHandler.RELATION_ALLEN_7);

    logger.debug('Testing CONTAINS in 7 relations, epsilon: ' + str(epsilon) + ', max gap: ' + str(maxGap))

    sti1 = SymbolicTimeInterval(1, 5, 'A', 345);
    sti2 = SymbolicTimeInterval(2, 4, 'B', 567);

    checkRelation(rh, sti1, sti2, epsilon, maxGap, AllenSevenRelationEngine.CONTAIN);

def checkRealtion7FinishedBy(epsilon, maxGap):

    rh = RelationHandler(RelationHandler.RELATION_ALLEN_7);

    logger.debug('Testing FINISH_BY in 7 relations, epsilon: ' + str(epsilon) + ', max gap: ' + str(maxGap))

    sti1 = SymbolicTimeInterval(1, 5, 'A', 345);
    sti2 = SymbolicTimeInterval(3, 5, 'B', 567);

    checkRelation(rh, sti1, sti2, epsilon, maxGap, AllenSevenRelationEngine.FINISHBY);

def checkRealtion7Equals(epsilon, maxGap):

    rh = RelationHandler(RelationHandler.RELATION_ALLEN_7);

    logger.debug('Testing EQUALS in 7 relations, epsilon: ' + str(epsilon) + ', max gap: ' + str(maxGap))

    sti1 = SymbolicTimeInterval(1, 5, 'A', 345);
    sti2 = SymbolicTimeInterval(1, 5, 'B', 567);

    checkRelation(rh, sti1, sti2, epsilon, maxGap, AllenSevenRelationEngine.EQUAL);

def checkRealtion7Starts(epsilon, maxGap):

    rh = RelationHandler(RelationHandler.RELATION_ALLEN_7);

    logger.debug('Testing STARTS in 7 relations, epsilon: ' + str(epsilon) + ', max gap: ' + str(maxGap))

    sti1 = SymbolicTimeInterval(1, 2, 'A', 345);
    sti2 = SymbolicTimeInterval(1, 5, 'B', 567);

    checkRelation(rh, sti1, sti2, epsilon, maxGap, AllenSevenRelationEngine.STARTS);

def check_allen_7_transitivity_table_init():
    allenT = AllenSevenRelationEngine();
    candidates = None;
    for i in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.EQUAL + 1):
        for j in range(AllenSevenRelationEngine.BEFORE, AllenSevenRelationEngine.EQUAL + 1):
            candidates = allenT.get_transitivity_list(i, j);
            if candidates == None or len(candidates) == 0:
                logger.error('[FAILED] not valid state in allen 7 transitivity table');

    #allenT.print_transitivity_table();
    logger.info('[PASSED] valid state in allen 7 transitivity table');

epsilon = 0.1;

maxGap = 6;

checkNotInGap(epsilon, maxGap);

checkRealtion7Before(epsilon, maxGap);

checkRealtion7Meets(epsilon, maxGap);

checkRealtion7Overlaps(epsilon, maxGap);

checkRealtion7FinishedBy(epsilon, maxGap);

checkRealtion7Contains(epsilon, maxGap);

checkRealtion7Starts(epsilon, maxGap);

checkRealtion7Equals(epsilon, maxGap);

check_allen_7_transitivity_table_init();


