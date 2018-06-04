from KarmaLego.KarmaLego_Framework.Karma import Karma
from KarmaLego.KarmaLego_Framework.Lego import Lego
from KarmaLego.TIRPsDetection_Framework.TIRPsDetection import TIRPsDetection

NUM_COMMA = 2


def run_KL(input_path,output_folder,epsilon,max_gap,vertical_support):
    output_path = output_folder
    suportVec = float(vertical_support)
    num_relations = 7
    num_symbols = count_symbols(input_path,output_path)
    max_gap = float(max_gap)
    epsilon = float(epsilon)
    karma = Karma(min_ver_support=suportVec, num_relations=num_relations, max_gap=max_gap, epsilon=epsilon)
    karma.fit(input_path, num_comma=NUM_COMMA,num_of_bins=num_symbols)
    lego = Lego(karma)
    lego.fit()
    lego.print_frequent_tirps(output_path)


def count_symbols(input_path,output_path):
    iter = 0
    entities_count = 0
    symbol_occurence = {}
    with open(input_path) as in_file, open(output_path, 'w') as out_file:
        for line in in_file:
            if iter == 0:
                pass
            elif iter == 1:
                entities_count = line.split(',')[-1]
            elif iter % 2 == 0:
                pass
            else:
                split_line = line.split(';')
                split_line = [int(x.split(',')[NUM_COMMA]) for x in split_line]
                for symbol in split_line:
                    if symbol in symbol_occurence:
                        symbol_occurence[symbol] += 1
                    else:
                        symbol_occurence[symbol] = 1
            iter += 1

        for symbol in symbol_occurence:
            out_file.write("1 %s- \0. 0 %s\n" % (symbol,entities_count))

    return len(symbol_occurence.keys())


if __name__ == "__main__":
    for i in reversed(range(1,10)):
        run_KL(r"C:\Users\Daniel Rejabek\PycharmProjects\Discretisation\datasets\FAAgeGroup_F3\EQW\3_2\karma_input_EQW_3_Class2.kcsv", r"C:\Users\Daniel Rejabek\PycharmProjects\Discretisation\datasets\FAAgeGroup_F3\EQW\3_2",0,3,i/10)
