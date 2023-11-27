# -*- coding: utf-8 -*-
"""
Copyright Antonia Baies
baies.antonia@gmail.com

This file is part of Loop Detection.
"""

from loop_detection.set_rep.range import Range
from typing import Union


class Combination:
    """
    Class used for the atom computation in get_UC_basic and get_UC
    Represents a combination of rules

    Parameters
    ----------
    r : Rule
        rule followed by the combination
    comp : list, default = []
        list of the name of rules which compose the combination

    Attributes
    ----------
    rule : Rule
    sup : set
        set of combinations that include the rule of the combination
    cont : set
        set of rules that contain the rule of the combination
    atsize : int
        size of the atom representated by the combination
    parent : Combination
        smallest combination such that self & parent is non empty
    covered: bool
    comp : list

    Examples
    --------
    >>> r1 = Range(1, 10)
    >>> r2 = Range(2, 12)
    >>> combi1 = Combination(r1, ['r1'])
    >>> combi2 = Combination(r2, ['r2'])
    >>> (combi1 & combi2).get_name()
    'r1 & r2'

    """

    def __init__(self, r, comp=[]):
        self.rule = r
        self.sup = set()  # set of combinations that include r
        self.cont = set()  # set of rules that contain r
        self.atsize = r.get_card()
        self.parent: Union[Combination, None] = None  # smallest combination such that self & parent is non-empty, by default itself
        self.covered = False
        self.comp = comp  # keep track of the rules that compose the current rule

    def get_name(self):
        if len(self.comp) == 0:
            return 'unknown'
        res = ''
        for i, c in enumerate(self.comp):
            if i != len(self.comp) - 1:
                res += c + " & "
            else:
                res += c
        return res

    def __and__(self, other):
        comp = self.comp + other.comp
        return Combination((self.rule & other.rule), comp)

    def __eq__(self, other):
        return self.rule == other.rule

    def __hash__(self):
        return hash(self.rule)

    def __repr__(self):
        return repr(self.rule)

    def __lt__(self, other):
        return self.rule < other.rule
