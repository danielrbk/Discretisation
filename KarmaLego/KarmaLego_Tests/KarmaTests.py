from KarmaLego.KarmaLego_Framework.Karma import Karma

import logging

from KarmaLego.KarmaLego_Framework.RelationHandler import AllenSevenRelationEngine
from KarmaLego.KarmaLego_Framework.SymbolicTimeInterval import SymbolicTimeInterval

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('KarmaTests')
logger.setLevel(20)

def test_load_file_simple():

    suportVec = 0.5;
    logger.debug('loading file for karma with support vec value: '+str(suportVec))
    karma = Karma(suportVec);
    karma.fit('../KarmaLego_TestsData/DiabetesEQW_3_Class1_with_mapping.csv')

def test_get_all_pairs():
    suportVec = 0.5;
    logger.debug('loading file for karma with support vec value: ' + str(suportVec))
    karma = Karma(suportVec);
    karma.fit('../KarmaLego_TestsData/single_entity_2_bins.csv')
    karma.get_all_pairs_mapped_by_entity_id(1, 2, 0);

def test_get_pairs():
    suportVec = 0.5;
    logger.debug('loading file for karma with support vec value: ' + str(suportVec))
    karma = Karma(suportVec);
    karma.fit('../KarmaLego_TestsData/single_entity_2_bins.csv')
    sti = SymbolicTimeInterval(0,2,1);
    pairs = karma.get_pairs(1,2,0,1,sti);

    if 2 == len(pairs):
        logger.info('[PASSED] pairs fetched '+str(pairs));
    else:
        logger.info('[FAILED] pairs not fetched - '+str(pairs));


def test_is_pair_exist():
    suportVec = 0.5;
    logger.debug('loading file for karma with support vec value: ' + str(suportVec))
    karma = Karma(suportVec);
    karma.fit('../KarmaLego_TestsData/single_entity_2_bins.csv')
    sti_a = SymbolicTimeInterval(0, 2, 1);
    sti_b = SymbolicTimeInterval(4, 6, 2);
    if karma.is_pair_exist(0, 1, sti_a, sti_b):
        logger.info('[PASSED] pair exist '+str(sti_a)+' '+str(sti_b));
    else:
        logger.info('[FAILED] pair dont exist '+str(sti_a)+' '+str(sti_b));

def test_get_relations_for_two_symbols():
    suportVec = 0.5;
    logger.debug('loading file for karma with support vec value: ' + str(suportVec))
    karma = Karma(suportVec);
    karma.fit('../KarmaLego_TestsData/single_entity_2_bins.csv')

    relations = karma.get_relations_for_two_symbols(1, 2);

    if len(relations) == 1 and relations[0] == AllenSevenRelationEngine.BEFORE:
        logger.info('[PASSED] relations fetched ' + str(relations));
    else:
        logger.info('[FAILED] relations not fetched' + str(relations));

def test_load_file():

    suportVec = 0.5;
    logger.debug('loading file for karma with support vec value: '+str(suportVec))
    karma = Karma(suportVec);
    karma.fit('../KarmaLego_TestsData/DiabetesEQW_3_Class1_with_mapping.csv',True)
    logger.info('[PASSED] karma build for skipped followers ');

test_get_all_pairs();
test_get_pairs();
test_is_pair_exist();
test_get_relations_for_two_symbols();
test_load_file();