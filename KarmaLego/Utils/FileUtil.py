from sklearn.model_selection import KFold
from KarmaLego.KarmaLego_Framework.RunKarmaLego import *
from KarmaLego.TIRPsDetection_Framework.TIRPsDetection import *
from KarmaLego.KarmaLego_Framework.TIRPsFeatureExraction import *
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score


def get_file_indexes(lines):
    """
    return the number of lines as indexes from the first entity row
    each line in indexes is one entity and has two indexes,
    one for the the entity id and second for its time intervals.
    Moreover it returns the start lines from the original file before the first entity row
    :param lines: list of lines in the original file
    :return: start_lines - list of the start lines
             indexes -array of indexes to split
    """
    starts = [n for n, l in enumerate(lines) if l.startswith('numberOfEntities')]
    if len(starts)==0:
        start_index=0
    else:
        start_index=starts[0]
    start_lines=lines[0:start_index+1]
    indexes=np.array([[i,i+1] for i in range (start_index+1,len(lines),2)])
    return start_lines,indexes


def get_folds_files(indexes,train_indices,test_indices,start_lines,lines, iteration,file_path):
    """
    this method creates new files for discovery and detection of tirps (train and test) by the given indices
     for each file, the method returns the new files with suffix of train/test and number of iteration
    :param indexes: array of lines indexes from the original  file
    :param train_indices: the train indices indexes
    :param test_indices: the test indices indexes
    :param start_lines: list of strings - the start lines in the original file
    :param lines: the readed lines from the original file
    :param iteration: int, number of iteration
    :param file_path: string, the original file path
    :return: train_file - the path of the train data,test_file - the path for the test data
    """
    prefix=file_path.replace(".csv","")
    train_file=prefix+"_train_"+str(iteration)+".csv"
    test_file = prefix +"_test_"+ str(iteration)+".csv"

    train_indexes = [list(indexes[i]) for i in train_indices]
    test_indexes = [list(indexes[i]) for i in test_indices]

    train_indexes_flat = [item for sublist in train_indexes for item in sublist]
    test_indexes_flat = [item for sublist in test_indexes for item in sublist]

    train_lines=start_lines+[lines[i] for i in train_indexes_flat]
    test_lines = start_lines + [lines[i] for i in test_indexes_flat]

    with open(train_file, 'w') as f:
        f.writelines(train_lines)
    with open(test_file, 'w') as f:
        f.writelines(test_lines)
    return train_file,test_file

def drop_recurrences_of_tirps(list_with_recurences,num_of_relations):
    tirp_dictionary = {}
    tirps_list = []
    for tirp in (list_with_recurences):
        tirp_dictionary[tirp.get_tirp_name(num_of_relations)] = tirp
    for tirp_name,tirp in tirp_dictionary.items():
        tirps_list.append(tirp)########################
    return  tirps_list

def demi_tirps(list_tirp):
    demi_tirps=[]
    for tirp in list_tirp:
        demi_tirps.append(tirp.hollow_copy())
    return demi_tirps

def CV_example(file_path_class_0,file_path_class_1,prefix_matrix,k=3,num_of_relations=7,max_gap=1,representation='HS',min_ver_support=0.6):
    """
    This method runs a k-fold cross-validation experiment, at each fold frequent TIRPs are found using KarmaLego framework
    for each class (class0, class1). Then, a feature matrix is generated from the train set and the classifier is fit to
     it. afterwards, a feature matrix is generated from the test for the classifier.
    :param file_path_class_0:  string, the path to the symbolic time intervals of calss 0
    :param file_path_class_1:  string, the path to the symbolic time intervals of calss 0
    :param prefix_matrix: string, part of the path to the train/test matrix
    :param k: number of folds
    :return: None
    """
    with open(file_path_class_0) as f:
        lines_class_0 = f.readlines()
        start_lines_0,indexes_class_0=get_file_indexes(lines_class_0)
    with open(file_path_class_1) as f:
        lines_class_1 = f.readlines()
        start_lines_1,indexes_class_1=get_file_indexes(lines_class_1)
    kf = KFold(n_splits=k)
    class_0_folds=list(kf.split(indexes_class_0))
    class_1_folds = list(kf.split(indexes_class_1))
    tirp_detection_obj = TIRPsDetection()
    tirp_feature_ext_obj=TIRPsFeatureExtraction()
    #AUC
    LogisticRegression_AUC_list=[]
    SVM_AUC_list=[]
    RandomForest_AUC_list=[]
    #Accuracy
    LogisticRegression_accuracy = []
    SVM_accuracy = []
    RandomForest_accuracy = []
    #Precision
    LogisticRegression_precision = []
    SVM_precision = []
    RandomForest_precision = []
    #Recall
    LogisticRegression_recall = []
    SVM_recall = []
    RandomForest_recall = []
    for i in range(k):
        train_file_class_0,test_file_class_0=get_folds_files(indexes=indexes_class_0,
                                                             train_indices=class_0_folds[i][0],
                                                             test_indices=class_0_folds[i][1],
                                                             start_lines=start_lines_0,
                                                             lines=lines_class_0,iteration=i,file_path=file_path_class_0)
        train_file_class_1, test_file_class_1 = get_folds_files(indexes=indexes_class_1,
                                                                train_indices=class_1_folds[i][0],
                                                                test_indices=class_1_folds[i][1],
                                                                start_lines=start_lines_1, lines=lines_class_1,
                                                                iteration=i, file_path=file_path_class_1)
        lego_0=runKarmaLego(time_intervals_path=train_file_class_0,min_ver_support=0.5,num_relations=7,max_gap=15,label=0,num_comma=3)
        tirps_class_0=lego_0.frequent_tirps
        lego_1 = runKarmaLego(time_intervals_path=train_file_class_1, min_ver_support=0.5, num_relations=7,max_gap=15,label=0,num_comma=3)
        tirps_class_1 = lego_1.frequent_tirps
        demi_tirps_class_0 = demi_tirps(tirps_class_0)
        demi_tirps_class_1 = demi_tirps(tirps_class_1)
        #tirps matrix for train
        detected_tirps_class_0_in_train=tirp_detection_obj.Sequential_TIRPs_Detection_multiply_entities(frequent_tirps=drop_recurrences_of_tirps(tirps_class_0+tirps_class_1,num_of_relations),#############
                                                                                               time_intervals_entities_path=train_file_class_0,
                                                                                               max_gap=max_gap,
                                                                                               epsilon=0,num_comma=3)
        matrix_class_0_train=tirp_feature_ext_obj.getMatrixForModeling(tirps=drop_recurrences_of_tirps(demi_tirps_class_0+demi_tirps_class_1+detected_tirps_class_0_in_train,num_of_relations),
                                                  entities_list=list(tirp_detection_obj._entities_map_to_detect.keys()),
                                                  representation=representation,num_of_relations=7,label=0)

        detected_tirps_class_1_in_train = tirp_detection_obj.Sequential_TIRPs_Detection_multiply_entities(frequent_tirps=drop_recurrences_of_tirps(tirps_class_0+tirps_class_1,num_of_relations),
                                                                                                time_intervals_entities_path=train_file_class_1,
                                                                                                 max_gap=max_gap,
                                                                                                epsilon=0,num_comma=3)
        matrix_class_1_train=tirp_feature_ext_obj.getMatrixForModeling(tirps=drop_recurrences_of_tirps(demi_tirps_class_0+demi_tirps_class_1+detected_tirps_class_1_in_train,num_of_relations),
                                                  entities_list=list(tirp_detection_obj._entities_map_to_detect.keys()),
                                                  representation=representation,num_of_relations=7, label=1)

        tirps_matrix_for_train=tirp_feature_ext_obj.concat_matrix_classes([matrix_class_0_train,matrix_class_1_train])
        tirps_matrix_for_train.to_csv(prefix_matrix +'_' +'train'+'_' + str(i) + '.csv')
        #tirps matrix for test
        detected_tirps_class_0_in_test=tirp_detection_obj.Sequential_TIRPs_Detection_multiply_entities(frequent_tirps=drop_recurrences_of_tirps(tirps_class_0+tirps_class_1,num_of_relations),
                                                                                               time_intervals_entities_path=test_file_class_0,
                                                                                               max_gap=max_gap,
                                                                                               epsilon=0,num_comma=3)
        matrix_class_0_test=tirp_feature_ext_obj.getMatrixForModeling(tirps=drop_recurrences_of_tirps(demi_tirps_class_0+demi_tirps_class_1+detected_tirps_class_0_in_test,num_of_relations),
                                                  entities_list=list(tirp_detection_obj._entities_map_to_detect.keys()),
                                                  representation=representation,num_of_relations=7,label=0)
        detected_tirps_class_1_in_test = tirp_detection_obj.Sequential_TIRPs_Detection_multiply_entities(frequent_tirps=drop_recurrences_of_tirps(tirps_class_0+tirps_class_1,num_of_relations),
                                                                                                time_intervals_entities_path=test_file_class_1,
                                                                                                 max_gap=max_gap,
                                                                                                epsilon=0,num_comma=3)
        matrix_class_1_test=tirp_feature_ext_obj.getMatrixForModeling(tirps=drop_recurrences_of_tirps(demi_tirps_class_0+demi_tirps_class_1+detected_tirps_class_1_in_test,num_of_relations),
                                                  entities_list=list(tirp_detection_obj._entities_map_to_detect.keys()),
                                                  representation=representation,num_of_relations=7,label=1)
        tirps_matrix_for_test=tirp_feature_ext_obj.concat_matrix_classes([matrix_class_0_test,matrix_class_1_test])
        tirps_matrix_for_test.to_csv(prefix_matrix +'_' +'test'+ '_' + str(i) + '.csv')

        with open(prefix_matrix +'_' +'test'+ '_' + str(i) + '.csv') as f:
            h = f.readline()
            columns = h.count(',') + 1
            f.close()

        if columns>2:
            # pre-processing  for classifier
            X_train = tirps_matrix_for_train.iloc[:, :-1]
            y_train= tirps_matrix_for_train.iloc[:, -1]
            X_test = tirps_matrix_for_test.iloc[:, :-1]
            y_test= tirps_matrix_for_test.iloc[:, -1]

            #LogisticRegression
            model_obj = LogisticRegression()
            model_obj.fit(X_train, y_train)
            y_pred = model_obj.predict_proba(X_test)[:,1]
            y_pred_binary = model_obj.predict(X_test)
            #  classifier accuracy
            fpr, tpr, thresholds = metrics.roc_curve(y_true=y_test, y_score=y_pred)
            auc = np.trapz(tpr, fpr)
            LogisticRegression_AUC_list.append(auc)
            LogisticRegression_accuracy.append(accuracy_score(y_test, y_pred_binary))
            LogisticRegression_precision.append(precision_score(y_test, y_pred_binary))
            LogisticRegression_recall.append(recall_score(y_test, y_pred_binary))
            print('LogisticRegression_AUC_list, Fold: {}, AUC: {}'.format(i,auc))

            # SVM
            model_obj = svm.SVC(probability=True)
            model_obj.fit(X_train, y_train)
            y_pred = model_obj.predict_proba(X_test)[:,1]
            y_pred_binary = model_obj.predict(X_test)
            #  classifier accuracy
            fpr, tpr, thresholds = metrics.roc_curve(y_true=y_test, y_score=y_pred)
            auc = np.trapz(tpr, fpr)
            SVM_AUC_list.append(auc)
            SVM_accuracy.append(accuracy_score(y_test, y_pred_binary))
            SVM_precision.append(precision_score(y_test, y_pred_binary))
            SVM_recall.append(recall_score(y_test, y_pred_binary))
            print('SVM_AUC_list, Fold: {}, AUC: {}'.format(i, auc))

            # RandomForest
            model_obj = RandomForestClassifier(random_state=100)
            model_obj.fit(X_train, y_train)
            y_pred = model_obj.predict_proba(X_test)[:, 1]
            y_pred_binary = model_obj.predict(X_test)
            #  classifier accuracy
            fpr, tpr, thresholds = metrics.roc_curve(y_true=y_test, y_score=y_pred)
            auc = np.trapz(tpr, fpr)
            RandomForest_AUC_list.append(auc)
            RandomForest_accuracy.append(accuracy_score(y_test, y_pred_binary))
            RandomForest_precision.append(precision_score(y_test, y_pred_binary))
            RandomForest_recall.append(recall_score(y_test, y_pred_binary))
            print('RandomForest_AUC_list, Fold: {}, AUC: {}'.format(i, auc))

    if columns > 2:
        # LogisticRegression- the mean AUC and the 95% confidence interval
        print("LogisticRegression AUC: %0.2f (+/- %0.2f)" % (np.mean(LogisticRegression_AUC_list), np.std(LogisticRegression_AUC_list) * 2))
        # SVM- the mean AUC and the 95% confidence interval
        print("SVM AUC: %0.2f (+/- %0.2f)" % (np.mean(SVM_AUC_list), np.std(SVM_AUC_list) * 2))
        # RandomForest- the mean AUC and the 95% confidence interval
        print("RandomForest AUC: %0.2f (+/- %0.2f)" % (np.mean(RandomForest_AUC_list), np.std(RandomForest_AUC_list) * 2))
        # The mean accuracy and the 95% confidence interval
        print("LogisticRegression Accuracy: %0.2f (+/- %0.2f)" % (np.mean(LogisticRegression_accuracy), np.std(LogisticRegression_accuracy) * 2))
        # The mean accuracy and the 95% confidence interval
        print("SVM Accuracy: %0.2f (+/- %0.2f)" % (np.mean(SVM_accuracy), np.std(SVM_accuracy) * 2))
        # The mean accuracy and the 95% confidence interval
        print("RandomForest Accuracy: %0.2f (+/- %0.2f)" % (np.mean(RandomForest_accuracy), np.std(RandomForest_accuracy) * 2))
        # The mean Precision and the 95% confidence interval
        print("LogisticRegression Precision: %0.2f (+/- %0.2f)" % (np.mean(LogisticRegression_precision), np.std(LogisticRegression_precision) * 2))
        # The mean Precision and the 95% confidence interval
        print("SVM Precision: %0.2f (+/- %0.2f)" % (np.mean(SVM_precision), np.std(SVM_precision) * 2))
        # The mean Precision and the 95% confidence interval
        print("RandomForest Precision: %0.2f (+/- %0.2f)" % (np.mean(RandomForest_precision), np.std(RandomForest_precision) * 2))
        # The mean recall and the 95% confidence interval
        print("LogisticRegression Recall: %0.2f (+/- %0.2f)" % (np.mean(LogisticRegression_recall), np.std(LogisticRegression_recall) * 2))
        # The mean recall and the 95% confidence interval
        print("SVM Recall: %0.2f (+/- %0.2f)" % (np.mean(SVM_recall), np.std(SVM_recall) * 2))
        # The mean recall and the 95% confidence interval
        print("RandomForest Recall: %0.2f (+/- %0.2f)" % (np.mean(RandomForest_recall), np.std(RandomForest_recall) * 2))





#CV_example('C:/Users/user/PycharmProjects/similarityKarmalEGO/data_sets/icu/SAX_OUT_TEST_Class0.txt','C:/Users/user/PycharmProjects/similarityKarmalEGO/data_sets/icu/SAX_OUT_TEST_Class1.txt',
#            'C:/Users/user/PycharmProjects/similarityKarmalEGO/data_sets/icu/matrix',max_gap=1,representation='HS',min_ver_support=0.8)
