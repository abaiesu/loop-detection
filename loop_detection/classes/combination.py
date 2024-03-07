class Combination():

    """
    Class used for the atom computation

    Attributes
    ----------
    r : Rule
        rule followed by the combination

    comp : list, default = []
        list of rules which compose the combintation

    """
    def __init__(self, r, comp = set()):
        self.rule = r
        self.sup = set() # list of combinations that contain r
        self.cont = [] # list of rules that contain r
        self.atsize = r.get_card()
        self.parent = None # combi minimal for inclusion = smallest combi such that self & parent is non empty
        self.covered = False
        self.comp = comp # keep track of the rules that compose the current rule

    def get_name(self):
        if len(self.comp) == 0:
            return 'unknown'
        res = ''
        for i, c in enumerate(self.comp):
            if i != len(self.comp) -1:
                res += c + " & "
            else:
                res += c
        return res

    def is_member(self, point):
        return self.rule.is_member(point)

    def __and__(self, other):
        comp = self.comp | other.comp
        return Combination((self.rule&other.rule), comp)

    def __eq__(self, other):
        return self.rule == other.rule #and self.get_name() == other.get_name()

    def __hash__(self):
        return hash(self.rule)

    def __repr__(self):
        return repr(self.rule)

    def __lt__(self, other):
        return self.rule < other.rule

