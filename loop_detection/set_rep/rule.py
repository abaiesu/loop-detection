# -*- coding: utf-8 -*-
"""
Copyright Antonia Baies
baies.antonia@gmail.com

This file is part of Loop Detection.
"""


class Rule:
    """
    Superclass for all the rules : Range, WildcardExpr, Multifields

    Parameters
    ----------
    rule : tuple OR str
        tuple if Range
        str if WildcardExpr
    max_card : int
        maximum cardinality of a rule
        in the context of forwarding rules, is used to retrieve the base rule
    field : str
        string for the name of the rule (IP source, port range...)

    """

    def __init__(self, rule, max_card, field):
        self.empty_flag = 1 if rule is None else 0
        self.field = field
        self.max_card = max_card
        self.card = 0

    def __and__(self, other):
        raise NotImplementedError

    def __lt__(self, other):
        raise NotImplementedError

    def is_member(self, point):
        raise NotImplementedError

    def get_card(self):
        raise NotImplementedError
