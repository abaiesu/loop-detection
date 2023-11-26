# -*- coding: utf-8 -*-
"""
Copyright Antonia Baies
baies.antonia@gmail.com

This file is part of Loop Detection.
"""

import re
import math

from loop_detection.set_rep.rule import Rule


class WildcardExpr(Rule):
    """
    Class for wildcard expression rule representation

    Attributes
    ----------
    string : str
        string on the characters : {0, 1, *}
        valid example : 1*001
        invalid example : 1.021
    max_card : int, default = infinity
    field : None

    Examples
    --------
        >>> r1 = WildcardExpr("*10*")
        >>> r2 = WildcardExpr("*1*1")
        >>> r1 & r2
        *101
        >>> WildcardExpr('*101') < r1
        True
        >>> r1.get_card()
        4

    """

    def __init__(self, string, max_card=float('inf'), field=None):
        super().__init__(string, max_card, field)
        self.expr = string
        if string is not None:
            pattern = r'[^01*]'
            match = re.search(pattern, string)
            if match is not None:
                raise ValueError('The alphabet for the wildcard expression is : {0, 1, *}')
            if self.max_card < float('inf') and len(string) > math.ceil(math.log2(self.max_card)):
                raise ValueError(f'The maximum length of an expression is {math.ceil(math.log2(self.max_card + 1))}')
            count = self.expr.count('*')
            if len(self.expr) > 1:  # avoid the wildcard * = any
                card = 2 ** count
            else:
                card = max_card
            self.card = card

    def __repr__(self):
        return self.expr if self.expr is not None else '∅'

    def __lt__(self, other):

        """
        Check if self is included in other (equality is accepted)

        Parameters
        ---------
        other : WildcardExpr

        Returns
        -------
        bool
        """

        for i in range(len(self.expr)):
            if self.expr[i] == '1' and other.expr[i] == '0' or self.expr[i] == '0' and other.expr[i] == '1':
                return False
            if self.expr[i] == '*' and self.expr[i] != '*':
                return False
        return True

    def __eq__(self, other):
        if self.expr == other.expr:
            return True
        return False

    def __and__(self, other):

        """
        Returns the result of set intersection

        Parameters
        ---------
        other : WildcardExpr

        Returns
        -------
        WildcardExpr

        """

        if self.empty_flag | other.empty_flag:  # one of the sets is empty
            return WildcardExpr(None)

        if self.expr == '*':
            return other
        if other.expr == '*':
            return self

        if len(self.expr) != len(other.expr):
            raise ValueError("Expressions must have the same length for intersection.")

        result = ""
        for i in range(len(self.expr)):
            if self.expr[i] == other.expr[i]:  # 0-0 OR 1-1 OR *-*
                result += self.expr[i]
            elif self.expr[i] == '*':  # *-0 OR *-1
                result += other.expr[i]
            elif other.expr[i] == '*':  # 0-* OR 1-*
                result += self.expr[i]
            else:  # 0-1 OR 1-0
                return WildcardExpr(None)

        return WildcardExpr(result)

    def __hash__(self):
        return hash(self.expr)

    def get_card(self):
        return self.card

    def is_member(self, string_to_check):

        if self.empty_flag:
            return False
        elif self.expr == '*':
            return True
        elif len(self.expr) != len(string_to_check):  # the lengths don't match
            return False
        pattern = self.expr.replace('*', '.')
        regex = re.compile(pattern)
        return bool(regex.fullmatch(string_to_check))
