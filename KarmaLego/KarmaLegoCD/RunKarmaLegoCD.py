from KarmaLego.KarmaLego_Framework.Karma import Karma
from KarmaLego.KarmaLegoCD.NewLego import NewLego

def runKarmaLegoCD(class_a_path,class_b_path,min_ver_support,num_relations,max_gap,min_vs_gap, alpha, weights,num_comma):
    """
    this method runs all the process of KarmaLegoCD with all relevant inputs
    :param class_a_path: String, the time intervals file for class A
    :param class_b_path: String, the time intervals file for class B
    :param min_ver_support: float, the minimum vertical support value
    :param num_relations: int, number of relations
    :param max_gap: int, the max_gap between the intervals for creating the index
    :param min_vs_gap: float, the minimum vertical support threshold between the classes
    :param alpha: float, the minimum alpha for the statistical tests
    :param weights: list[float] the weight for the scoring function
    :return: newLego,  returns the NewLego object
    """
    karma_a = Karma(min_ver_support, num_relations=num_relations, max_gap=max_gap,label=0)
    karma_b = Karma(min_ver_support, num_relations=num_relations, max_gap=max_gap,label=1)
    karma_a.fit(class_a_path,num_comma=num_comma,min_vertical_support_for_trim=0.3)
    karma_b.fit(class_b_path,num_comma=num_comma,min_vertical_support_for_trim=0.3)
    newLego=NewLego(karma_a=karma_a,karma_b=karma_b,min_vs_gap=min_vs_gap,alpha=alpha,weights=weights)
    newLego.fit()
    return newLego
