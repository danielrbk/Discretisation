

class SymbolicTimeInterval(object):
    """
     Symbolic time Interval representing a time interval with start time and end time and corresponds to a given symbol.
    """


    def __init__(self, start_time, end_time, symbol, varId=None):
        self._start_time = start_time
        self._end_time = end_time
        self._symbol = symbol
        self._var_id = varId

    def __init__(self, start_time= None, end_time= None, symbol= None, varId=None):
        self._start_time = start_time
        self._end_time = end_time
        self._symbol = symbol
        self._var_id = varId

    def __eq__(self, other):
        return self._start_time == other._start_time and self._end_time == other._end_time and self._symbol == other._symbol;

    def getStartTime(self):
        return self._start_time

    def getEndTime(self):
        return self._end_time

    def getSymbol(self):
        return self._symbol

    def getVarID(self):
        return self._var_id

    def toString(self):
        return 'SymbolicTimeInterval: { Symbol'+str(self._symbol)+', startTime: '+str(self._start_time)+', endTime: '+str(self._end_time)+', varID: '+str(self._var_id)+'}';

    def copy(self):
        """
        create new SymbolicTimeInterval and copy all current variables
        :return: SymbolicTimeInterval,copy of this tirp
        """
        new_SymbolicTimeInterval = SymbolicTimeInterval()
        new_SymbolicTimeInterval._start_time = self._start_time
        new_SymbolicTimeInterval._end_time=self._end_time
        new_SymbolicTimeInterval._symbol = self._symbol
        new_SymbolicTimeInterval._var_id=self._var_id
        return new_SymbolicTimeInterval
