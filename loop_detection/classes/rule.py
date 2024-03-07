# -*- coding: utf-8 -*-
"""
Copyright Antonia Baies
baies.antonia@gmail.com

This file is part of Loop Detection.
"""


class Rule:
    """
    Abstract class for all the rules : Range, WildcardExpr, MultiField
    """

    def __init__(self, name, max_card, field):
        self.empty_flag = 1  # by default all new rules are empty
        self.field = field
        self.name = name
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
