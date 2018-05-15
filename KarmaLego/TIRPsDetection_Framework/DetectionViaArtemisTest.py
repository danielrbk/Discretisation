from KarmaLego_Framework.Karma import Karma
from KarmaLego_Framework.Lego import Lego
import logging
from TIRPsDetection_Framework.TIRPsDetection import TIRPsDetection
from TIRPsDetection_Framework.DetectionViaArtemis import DetectionViaArtemis
from KarmaLego_Framework.SymbolicTimeInterval import SymbolicTimeInterval
import more_itertools
import itertools
import pandas as pd
from sklearn.model_selection import KFold
from KarmaLego_Framework.RunKarmaLego import *
from TIRPsDetection_Framework.TIRPsDetection import *
from TIRPsDetection_Framework.DetectionViaArtemis import *
from KarmaLego_Framework.TIRPsFeatureExraction import *
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn.metrics import accuracy_score
import csv


FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('KarmaTests')
logger.setLevel(20)


def DetectionViaArtemisTest():
    tirps_detected_path='../KarmaLego_TestsData/tirps_detected_sequential_search.csv'
    suportVec = 0.5
    num_relations = 7
    max_gap = 30
    epsilon = 0
    logger.debug('loading file for karma with support vec value: ' + str(suportVec))
    karma = Karma(suportVec, num_relations=num_relations, max_gap=max_gap)
    karma.fit('../KarmaLego_TestsData/Example_Class0.csv', num_comma=2, num_of_bins=3, symbol_type='int')
    lego = Lego(karma)
    lego.fit()
    lego.print_frequent_tirps('../KarmaLego_TestsData/lego_TIRP_Artemis.csv')
    DetectionViaArtemis_obj = DetectionViaArtemis()
    Pattern_path = '../KarmaLego_TestsData/Example_Class0.csv'
    #DetectionViaArtemis_obj.parse_file_into_symbolic_time_intervals(Pattern_path, 2)
    #tirp_map_list_before, tirp_map_list_after=DetectionViaArtemis_obj.mapping_step_for_TIRP(lego.frequent_tirps[2])
    #entity_map_list_before, entity_map_list_after=DetectionViaArtemis_obj.mapping_step_for_symbolic_time_intervals(DetectionViaArtemis_obj._entities_map_to_detect[5])
    #DetectionViaArtemis_obj.Artemis(tirp_map_list_before,tirp_map_list_after,entity_map_list_before,entity_map_list_after)
    time_intervals_entities_path = '../KarmaLego_TestsData/Example_Class1.csv'
    tirps_detected=DetectionViaArtemis_obj.Sequential_TIRPs_Detection_multiply_entities(lego.frequent_tirps,time_intervals_entities_path,0.77,'AC',max_gap=max_gap)
    DetectionViaArtemis_obj.print_detected_tirps(tirps_detected_path,tirps_detected)
    return tirps_detected



#test = pd.read_csv('../KarmaLego_TestsData/matrix_test_1.csv')
#train = pd.read_csv('../KarmaLego_TestsData/matrix_train_1.csv')
# pre-processing  for classifier

#train.drop(train.columns[[0]], axis=1, inplace=True)
#test.drop(test.columns[[0]], axis=1, inplace=True)
#X_train = train.iloc[:, :-1]


#y_train= train.iloc[:, -1]
#print(X_train)
#print(y_train)
#X_test = test.iloc[:, :-1]
#y_test= test.iloc[:, -1]

            #NB classifier
#model_obj = MultinomialNB()
#model_obj.fit(X_train, y_train)
#y_pred = model_obj.predict(X_test)

#  classifier accuracy
#fpr, tpr, thresholds = metrics.roc_curve(y_true=y_test, y_score=y_pred, drop_intermediate=True)
#auc = np.trapz(tpr, fpr)
#print('AUC:', auc)
#print('Accuracy Score:', accuracy_score(y_test, y_pred))



tirps_detected=DetectionViaArtemisTest()

print("done")