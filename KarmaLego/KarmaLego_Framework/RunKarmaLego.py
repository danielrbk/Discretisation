from KarmaLego.KarmaLego_Framework.Karma import Karma
from KarmaLego.KarmaLego_Framework.Lego import Lego

def runKarmaLego(time_intervals_path,min_ver_support,num_relations,max_gap,label,max_tirp_length=5,num_comma=2,num_of_bins=3,symbol_type='int'):
    """
    this method runs  the process of KarmaLego with all relevant inputs
    :param time_intervals_path: String, the time intervals file
    :param class_b_path: String, the time intervals file for class
    :param min_ver_support: float, the minimum vertical support value
    :param num_relations: int, number of relations
    :param max_gap: int, the max_gap between the intervals for creating the index
    :return:
    """
    karma = Karma(min_ver_support, num_relations=num_relations, max_gap=max_gap,label=label)
    karma.fit(time_intervals_path,num_comma,num_of_bins,symbol_type)
    lego=Lego(karma,max_tirp_length)
    lego.fit()
    return lego
