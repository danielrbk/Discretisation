

class PredictiveTIRP (object):
    """
    Class for predictive TIRP , hold the TIRPs from the two classes
    """

    def __init__(self, tirp_a,tirp_b,score=0):
        self._tirp_a=tirp_a
        self._tirp_b=tirp_b
        self._score=score

