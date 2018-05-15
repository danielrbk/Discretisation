from KarmaLego_Framework.Karma import Karma
from KarmaLego_Framework.Lego import Lego
import logging
from TIRPsDetection_Framework.TIRPsDetection import TIRPsDetection
from KarmaLego_Framework.SymbolicTimeInterval import SymbolicTimeInterval

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('KarmaTests')
logger.setLevel(20)

def test_TIRPsDetection():
    tirps_detected_path='C:/Users/user/PycharmProjects/similarityKarmalEGO/data_sets/icu/nofar/detect.csv'
    suportVec = 0.5
    num_relations = 7
    max_gap = 15
    logger.debug('loading file for karma with support vec value: '+str(suportVec))
    karma = Karma(suportVec,num_relations=num_relations,max_gap=max_gap)
    karma.fit('C:/Users/user/PycharmProjects/similarityKarmalEGO/data_sets/icu/nofar/bug.csv')
    lego=Lego(karma)
    lego.fit()
    lego.print_frequent_tirps('C:/Users/user/PycharmProjects/similarityKarmalEGO/data_sets/icu/nofar/output_sequence4.csv')
    tirp_detection_obj= TIRPsDetection()
    time_intervals_entities_path='C:/Users/user/PycharmProjects/similarityKarmalEGO/data_sets/icu/nofar/bug.csv'
    #time_intervals_entities_path='../KarmaLego_TestsData/symbolic_time_intervals_of_3_entities.csv'
    tirps_detected=tirp_detection_obj.Sequential_TIRPs_Detection_multiply_entities(lego.frequent_tirps,time_intervals_entities_path,max_gap=max_gap)
    tirp_detection_obj.print_detected_tirps(tirps_detected_path,tirps_detected)
    return tirps_detected

tirps_detected=test_TIRPsDetection()
print("done")