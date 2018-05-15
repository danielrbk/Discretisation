from KarmaLego.KarmaLego_Framework.Karma import Karma
from KarmaLego.KarmaLego_Framework.Lego import Lego
import logging
from KarmaLego.KarmaLego_Framework.TIRP import TIRP

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('KarmaTests')
logger.setLevel(20)

def test_test_lego_fit():

    suportVec = 0.5
    num_relations = 7
    max_gap = 15
    logger.debug('loading file for karma with support vec value: '+str(suportVec))
    karma = Karma(suportVec,num_relations=num_relations,max_gap=max_gap)
    karma.fit('../KarmaLego_TestsData/DiabetesEQW_3_Class0_short.csv')
    lego=Lego(karma)
    lego.fit()
    lego.print_frequent_tirps('../KarmaLego_TestsData/DiabetesEQW_3_Class0_50_15_output_sequence.csv')
    depth = lego.tirps_tree_root.get_max_depth()
    leafs = lego.tirps_tree_root.get_all_leafs()
    logger.info('[PASSED] Lego fit completed, tree depth is: '+str(depth)+' with '+str(len(leafs))+" leafs");

def test_lego_generate_candidates():

    """

    the tested relations are the 7 allens as defined in RelationHandler

                | B | C | D |
              --|---|---|---|
              A | 2 |  2|  ?|
              --|---|---|---|
              B |   |  2|  ?|
              --|---|---|---|
              C |   |   |  2|

    should generate 5 matching candidates

    [[0,0,2],[0,1,2],[0,2,2],[1,2,2],[2,2,2]]

    for future tirps as:

                | B | C | D |     | B | C | D |    | B | C | D |     | B | C | D |    | B | C | D |
              --|---|---|---|   --|---|---|---|  --|---|---|---|   --|---|---|---|  --|---|---|---|
              A | 2 |  2|  0|   A | 2 |  2|  0|  A | 2 |  2|  0|   A | 2 |  2|  1|  A | 2 |  2|  2|
              --|---|---|---|   --|---|---|---|  --|---|---|---|   --|---|---|---|  --|---|---|---|
              B |   |  2|  0|   B |   |  2|  1|  B |   |  2|  2|   B |   |  2|  2|  B |   |  2|  2|
              --|---|---|---|   --|---|---|---|  --|---|---|---|   --|---|---|---|  --|---|---|---|
              C |   |   |  2|   C |   |   |  2|  C |   |   |  2|   C |   |   |  2|  C |   |   |  2|

              .....

    recursion tree should be:

     0   0  0  1  2
     |   |  \  |  /
     |   |   \ | /
     |   |    \|/
     0   1    2
     \   |   /
      \  |  /
       \ | /
        \|/
         2

    """
    expected = [[0,0,2],[0,1,2],[0,2,2],[1,2,2],[2,2,2]]
    result = True
    reason = 'as expected'

    tirp = TIRP('A','B', 2)
    tirp._symbols.append('C')
    tirp._tirp_matrix.extend([2, 2])

    lego = Lego(Karma(1))

    # expending with overlap (2) when others are overlap too
    candidates = lego.generate_candidats(tirp, 2)

    if len(candidates) != len(expected):
        result = False
        reason = 'candidates amount not match'
    elif candidates != expected:
        result = False
        reason = 'candidates not as expected'

    if result:
        logger.info('[PASSED] Lego candidates generation success: '+reason);
    else:
        logger.error('[FAILED] Lego candidates generation failed, reason: '+reason);


#test_lego_generate_candidates();

test_test_lego_fit()