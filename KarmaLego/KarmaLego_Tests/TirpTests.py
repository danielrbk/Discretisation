from KarmaLego.KarmaLego_Framework.TirpMatrix import TirpMatrix

import logging

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('KarmaTests')
logger.setLevel(20)

def test_tirp_matrix_simple_create():

    t = TirpMatrix('r1');

    result = True;
    reason = 'all good';

    if len(t._relations) != 1 or t._relations[0] != 'r1':
        result = False;
        reason = 'relations not set';

    if result:
        logger.error('[PASSED] TIRP matrix creation: '+reason);
    else:
        logger.error('[FAILED] TIRP matrix creation: '+reason);

def test_tirp_matrix_copy():

    original = TirpMatrix('r1');

    t = original.copy();

    result = True;
    reason = 'all good';

    if len(t._relations) != 1 or t._relations[0] != 'r1':
        result = False;
        reason = 'relations not set';

    if result:
        logger.error('[PASSED] TIRP matrix copy: '+reason);
    else:
        logger.error('[FAILED] TIRP matrix copy: '+reason);

def test_tirp_matrix_get_all_direct_relations():
    matrix = TirpMatrix('r1');

    result = True;
    reason = 'all good';

    matrix.extend(['r2', 'r3']);

    if matrix._relations != ['r1', 'r2', 'r3']:
        result = False;
        reason = '1st extend failed';

    matrix.extend(['r4', 'r5', 'r6']);

    if result and matrix._relations != ['r1', 'r2', 'r4', 'r3', 'r5', 'r6']:
        result = False;
        reason = '2nd extend failed';

    matrix.extend(['r7','r8','r9','r10']);

    if result and matrix._relations != ['r1', 'r2','r4', 'r7', 'r3', 'r5', 'r8', 'r6', 'r9', 'r10']:
        result = False;
        reason = '3rd extend failed';

    relations = matrix.get_all_direct_relations();

    if result:
        logger.error('[PASSED] TIRP matrix extend: '+reason);
    else:
        logger.error('[FAILED] TIRP matrix extend: '+reason);



def test_tirp_matrix_extend():
    matrix = TirpMatrix('r1');

    result = True;
    reason = 'all good';

    matrix.extend(['r2','r3']);

    if matrix._relations != ['r1','r2','r3']:
        result = False;
        reason = '1st extend failed';

    matrix.extend(['r4', 'r5', 'r6']);

    if result and matrix._relations != ['r1','r2','r4', 'r3', 'r5', 'r6']:
        result = False;
        reason = '2nd extend failed';


    matrix.extend(['r7','r8','r9','r10']);

    if result and matrix._relations != ['r1', 'r2','r4', 'r7', 'r3', 'r5', 'r8', 'r6', 'r9', 'r10']:
        result = False;
        reason = '3rd extend failed';

    if result:
        logger.error('[PASSED] TIRP matrix extend: '+reason);
    else:
        logger.error('[FAILED] TIRP matrix extend: '+reason);

def test_tirp_matrix_get_relation_3_symbols():

    # matrix representing relations for [A, B, C]
    """
                | B | C  |
              --|---|----|
              A | r1| r2 |
              --|---|----|
              B |   | r3 |
              --|---|----|
    :return:
    """

    matrix = TirpMatrix('r1');

    result = True;
    reason = 'all good';

    matrix.extend(['r2','r3']);

    if matrix._relations != ['r1','r2','r3']:
        result = False;
        reason = '1st extend failed';

    # [A, B, C]
    # test relation fetch for A B
    relation = matrix.get_relation(0, 1);

    if result and relation != 'r1':
        result = False;
        reason = 'relation fetch for A B failed, got ['+relation+']';

    # [A, B, C]
    # test relation fetch for B C
    relation = matrix.get_relation(1, 2);

    if result and relation != 'r3':
        result = False;
        reason = 'relation fetch for B C failed, got ['+relation+']';

    # [A, B, C]
    # test relation fetch for B C
    relation = matrix.get_relation(0, 2);

    if result and relation != 'r2':
        result = False;
        reason = 'relation fetch for A C failed, got ['+relation+']';

    if result:
        logger.error('[PASSED] TIRP matrix 3 symbol fetch: '+reason);
    else:
        logger.error('[FAILED] TIRP matrix 3 symbol fetch: '+reason);

def test_tirp_matrix_get_relation_4_symbols():

    # matrix representing relations for [A, B, C, D]
    """
                | B | C | D |
              --|---|---|---|
              A | r1| r2| r4|
              --|---|---|---|
              B |   | r3| r5|
              --|---|---|---|
              C |   |   | r6|
    :return:
    """

    matrix = TirpMatrix('r1');

    result = True;
    reason = 'all good';

    matrix.extend(['r2','r3']);

    if matrix._relations != ['r1','r2','r3']:
        result = False;
        reason = '1st extend failed';

    matrix.extend(['r4', 'r5', 'r6']);

    if result and matrix._relations != ['r1','r2','r4', 'r3', 'r5', 'r6']:
        result = False;
        reason = '2nd extend failed';

    # [A, B, C, D]
    # test relation fetch for A B
    relation = matrix.get_relation(0, 1);

    if result and relation != 'r1':
        result = False;
        reason = 'relation fetch for A B failed, got ['+relation+']';

    # [A, B, C, D]
    # test relation fetch for A C
    relation = matrix.get_relation(0, 2);

    if result and relation != 'r2':
        result = False;
        reason = 'relation fetch for A C failed, got ['+relation+']';

    # [A, B, C, D]
    # test relation fetch for A D
    relation = matrix.get_relation(0, 3);

    if result and relation != 'r4':
        result = False;
        reason = 'relation fetch for A C failed, got ['+relation+']';

    # [A, B, C, D]
    # test relation fetch for B C
    relation = matrix.get_relation(1, 2);

    if result and relation != 'r3':
        result = False;
        reason = 'relation fetch for B C failed, got ['+relation+']';

    # [A, B, C, D]
    # test relation fetch for B D
    relation = matrix.get_relation(1, 3);

    if result and relation != 'r5':
        result = False;
        reason = 'relation fetch for B D failed, got ['+relation+']';

    # [A, B, C, D]
    # test relation fetch for C D
    relation = matrix.get_relation(2, 3);

    if result and relation != 'r6':
        result = False;
        reason = 'relation fetch for B D failed, got ['+relation+']';

    if result:
        logger.error('[PASSED] TIRP matrix 4 symbol fetch: '+reason);
    else:
        logger.error('[FAILED] TIRP matrix 4 symbol fetch: '+reason);

test_tirp_matrix_get_all_direct_relations();

test_tirp_matrix_simple_create();

test_tirp_matrix_copy();

test_tirp_matrix_extend();

test_tirp_matrix_get_relation_3_symbols();

test_tirp_matrix_get_relation_4_symbols();