
from scipy import stats
from KarmaLego.KarmaLego_Framework.TIRPsFeatureExraction import TIRPsFeatureExtraction
import numpy as np

class TIRPFeatureSelection (object):


    def __init__(self, min_vs_gap, alpha, weights):
        self._min_vs_gap = min_vs_gap
        self._alpha = alpha
        self._weights = weights

    def fit(self, c_a, c_b,c_a_vs, c_b_vs,entities_a, entities_b):
        feature_ext=TIRPsFeatureExtraction()
        is_predictive = False
        score = 0
        if c_a_vs==0  or c_b_vs==0 :
            if c_a_vs>0:
                score = self.getScore(c_a_vs)
                is_predictive = True
            else:
                score = self.getScore(c_b_vs)
                is_predictive = True
        else:
            vs_gap = abs(c_a_vs - c_b_vs)
            if vs_gap > self._min_vs_gap:
                score = self.getScore(c_a_vs, c_b_vs, vs_gap)
                is_predictive = True
            else:
                horizontal_suppost_a = feature_ext.getFeaturesListByTIRP(c_a,entities_a, 'HS')
                horizontal_suppost_b = feature_ext.getFeaturesListByTIRP(c_b,entities_b, 'HS')
                t, p_hs = stats.ttest_ind(horizontal_suppost_a, horizontal_suppost_b, equal_var=False)
                if p_hs <= self._alpha:
                    score = self.getScore(c_a_vs, c_b_vs, vs_gap, p_hs)
                    is_predictive = True
                else:
                    mean_duration_a = feature_ext.getFeaturesListByTIRP(c_a, entities_a,'MND')
                    mean_duration_b = feature_ext.getFeaturesListByTIRP(c_b,entities_b, 'MND')
                    t, p_mnd = stats.ttest_ind(mean_duration_a, mean_duration_b, equal_var=False)
                    if p_mnd <= self._alpha:
                        score = self.getScore(c_a_vs, c_b_vs, vs_gap, p_hs, p_mnd)
                        is_predictive = True
        return is_predictive,score



    def getScore(self, c_a_vs, c_b_vs=None, vs_gap=None, p_hs=None, p_mnd=None):
        score = 0
        if c_b_vs is None:
            score = sum(self._weights) * c_a_vs
        elif p_hs is None:
            score = self._weights[0] * ((c_a_vs + c_b_vs) / 2) + sum(self._weights[1:3]) * vs_gap
        elif p_mnd is None:
            score = self._weights[0] * ((c_a_vs + c_b_vs) / 2) + self._weights[1] * vs_gap + sum(self._weights[2:3]) * (
            1 - p_hs)
        else:
            score = self._weights[0] * ((c_a_vs + c_b_vs) / 2) + self._weights[1] * vs_gap + self._weights[2] * (
            1 - p_hs) + self._weights[2] * (1 - p_mnd)
        return score

    def getPredictiveTIRPSbyScore(self,class_legos):
        feature_names = []
        feature_scores = []
        class_0_tirps_names=[tirp._name for tirp in class_legos[0].frequent_tirps]
        class_1_tirps_names = [tirp._name for tirp in class_legos[1].frequent_tirps]
        tirps_names = list(set(class_0_tirps_names+class_1_tirps_names))
        for tirp_name in tirps_names:
            tirp_0=[tirp for tirp in class_legos[0].frequent_tirps if tirp._name==tirp_name]
            tirp_1 = [tirp for tirp in class_legos[1].frequent_tirps if tirp._name == tirp_name]
            if len(tirp_0)>0 and len(tirp_1)>0:
                tirp_0=tirp_0[0]
                tirp_1=tirp_1[0]
                c_a_vs=tirp_0.get_vertical_support()/len(class_legos[0]._karma._entities_map)
                c_b_vs=tirp_1.get_vertical_support()/len(class_legos[1]._karma._entities_map)
                is_predictive, score= self.fit( tirp_0, tirp_1,c_a_vs, c_b_vs,class_legos[0]._karma._entities_map.keys(), class_legos[1]._karma._entities_map.keys())
                if is_predictive:
                    feature_names.append(tirp_name)
                    feature_scores.append(score)
            elif len(tirp_0)>0:
                tirp_0 = tirp_0[0]
                c_a_vs = tirp_0.get_vertical_support() / len(class_legos[0]._karma._entities_map)
                score=self.getScore(c_a_vs)
                feature_names.append(tirp_name)
                feature_scores.append(score)
            elif len(tirp_1)>0:
                tirp_1 = tirp_1[0]
                c_b_vs = tirp_1.get_vertical_support() / len(class_legos[1]._karma._entities_map)
                score = self.getScore(c_b_vs)
                feature_names.append(tirp_name)
                feature_scores.append(score)
        feature_scores = np.array(feature_scores)
        arrinds = feature_scores.argsort()
        feature_names = np.array(feature_names)[arrinds[::-1]]
        return feature_names