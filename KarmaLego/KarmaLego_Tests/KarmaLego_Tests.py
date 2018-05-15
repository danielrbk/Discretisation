from KarmaLego.KarmaLego_Framework.RunKarmaLego import *
from KarmaLego.KarmaLego_Framework.TIRPsFeatureExraction import TIRPsFeatureExtraction

import logging
from KarmaLego.KarmaLego_Framework.TIRP import TIRP

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('KarmaTests')
logger.setLevel(20)

def test_get_matrix():

    suportVec = 0.5
    num_relations = 7
    max_gap = 15
    path='../KarmaLego_TestsData/DiabetesEQW_3_Class0_short.csv'
    lego=runKarmaLego(time_intervals_path=path,min_ver_support=suportVec,num_relations=num_relations,max_gap=15)
    features_ext_obj=TIRPsFeatureExtraction(lego._karma)
    matrix_hs=features_ext_obj.getMatrixForModeling(lego.frequent_tirps,"HS",7)
    matrix_hs.to_csv('../KarmaLego_TestsData/DiabetesEQW_3_Class0_50_15_matrix_hs.csv')

test_get_matrix()