def karma_to_karmav_format(path, output):
    lines = []
    with open(path) as karma:
        for line in karma:
            split_line = line.split( )
            relation_string = tuple([int(x) for x in split_line[1].split('-')[:-1]])
            count = int(split_line[0])
            if count == 1:
                property_string = " ".join(split_line[:5])
                lines.append((relation_string, property_string + " \n ;\n"))
            else:
                vertical_support = int(split_line[3])
                mean_horizontal_support = float(split_line[4])
                horizontal_support = int(vertical_support * mean_horizontal_support)
                property_string = " ".join(split_line[:3])
                time_string = ""
                entity_id = 0
                for i in range(5,len(split_line)):
                    if i%2 == 1:
                        entity_id = split_line[i]
                    else:
                        brackets = split_line[i]
                        num_in_entity = brackets.count('[') // count
                        from_index = 0
                        to_index = 0

                        for j in range(num_in_entity):
                            curr_index = from_index
                            for k in range(count):
                                curr_index = brackets.find(']',curr_index) + 1
                            time_string += "%s %s " % (entity_id, brackets[from_index:curr_index])
                            from_index = curr_index
                lines.append((relation_string, property_string + " %s %s \n" % (horizontal_support,vertical_support) + time_string + ";\n"))
    lines = sorted(lines, key=lambda x: x[0])
    lines = [x[1] for x in lines]
    with open(output, 'w') as o:
        o.writelines(lines)

if __name__ == "__main__":
    for i in reversed(range(1,10)):
        input_file = r"C:\Users\Daniel Rejabek\PycharmProjects\Discretisation\datasets\FAAgeGroup_F3\EQW\3_2\KARMALEGOV\epsilon%s_maxgap%s_vs%s.csv" % (0, 3,i/10)
        output_file = r"C:\Users\Daniel Rejabek\PycharmProjects\Discretisation\datasets\FAAgeGroup_F3\EQW\3_2\KARMALEGOV\epsilon%s_maxgap%s_vs%s.karma" % (0, 3,i/10)
        karma_to_karmav_format(input_file,output_file)