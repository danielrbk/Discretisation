from KarmaLego.KarmaLegoCD.RunKarmaLegoCD import runKarmaLegoCD


class_a_path='../KarmaLego_TestsData/DiabetesEQW_3_Class0_short.csv'
class_b_path='../KarmaLego_TestsData/DiabetesEQW_3_Class1_short.csv'
min_ver_support=0.5
num_relations=7
max_gap=15
min_vs_gap=0.1
alpha=0.05
weights=[0.5,0.2,0.1,0.1]
runKarmaLegoCD(class_a_path=class_a_path,class_b_path=class_b_path,min_ver_support=min_ver_support
               ,num_relations=num_relations,max_gap=max_gap,min_vs_gap=min_ver_support,alpha=alpha,weights=weights)
