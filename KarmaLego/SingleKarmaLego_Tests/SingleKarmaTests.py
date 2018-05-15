from KarmaLego_Framework.Karma import Karma
from SingleKarmaLego_Framework.SingleKarma import SingleKarma
import logging

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('SingleKarmaTests')
logger.setLevel(20)


def test_fit():
    suportVec = 0.5;
    logger.debug('loading file for karma with support vec value: ' + str(suportVec))
    karma = Karma(suportVec);
    karma.fit('../KarmaLego_TestsData/DiabetesEQW_3_Class1_with_mapping.csv', True)

    All_Entities_Mapings = karma._entities_map
    for entity in All_Entities_Mapings:
        sKarma = SingleKarma()
        sKarma.fit(True,entity,All_Entities_Mapings[entity],karma._var_to_symbols,karma._dharma_index)

    logger.info('[PASSED] SingleKarma build for all entities ');

test_fit()