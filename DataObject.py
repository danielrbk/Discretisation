# [variable, time, value]
from TimeInterval import TimeInterval

class DataObject(object):

    def __init__(self, data):
        sorted_data = sorted(data, key=lambda single_data_point: (single_data_point[0], single_data_point[1]))
        variables = set([x[0] for x in sorted_data])
        self.variable_to_values = {}
        for var in variables:
            self.variable_to_values[var] = [(x[1], x[2]) for x in sorted_data if x[0] == var]

    def __str__(self):
        string = "Data - ("
        strings = []
        for key in self.variable_to_values.keys():
            string += "%s: [" % key
            for l in self.variable_to_values[key]:
                strings.append("(Time: %s, Value: %s)" % (l[0], l[1]))
            string += ", ".join(strings) + "]  "
        string += ")"
        return string



data = DataObject([('a',TimeInterval(1,3),3),('a',TimeInterval(0,3),4),('b',TimeInterval(4,7),2),('a',TimeInterval(-1,3),3)])
print(data)