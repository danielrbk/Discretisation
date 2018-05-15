from KarmaLego.KarmaLego_Framework.Karma import Karma
from KarmaLego.KarmaLego_Framework.Lego import Lego
from KarmaLego.TIRPsDetection_Framework.TIRPsDetection import TIRPsDetection

NUM_COMMA = 2


def run_KL(input_path,output_folder,epsilon,max_gap,vertical_support):
    suportVec = float(vertical_support)
    num_relations = 7
    max_gap = float(max_gap)
    epsilon = float(epsilon)
    karma = Karma(min_ver_support=suportVec, num_relations=num_relations, max_gap=max_gap, epsilon=epsilon)
    karma.fit(input_path, num_comma=NUM_COMMA,num_of_bins=3)
    lego = Lego(karma)
    lego.fit()
    lego.print_frequent_tirps(output_folder + "\\epsilon%s_maxgap%s_vs%s.csv" % (epsilon, max_gap, vertical_support))

if __name__ == "__main__":
    for i in reversed(range(3,10)):
        run_KL(r"C:\Users\Daniel\Downloads\input.csv", r"C:\Users\Daniel\Downloads\output",0,3,i/10)
