# -*- coding: utf-8 -*-
"""
Copyright Antonia Baies
baies.antonia@gmail.com

This file is part of Loop Detection.
"""

from loop_detection.set_rep.rule import Rule
from loop_detection.set_rep.wildcardexpr import WildcardExpr


class Range(Rule):
    """
    Class for range rule representation

    Parameters
    ----------
    start : int
        start of the range (included)
    end : int
        end of the range (included)
    max_card : int, default = infinity
        maximum cardinality of the rule
    field : str, default = None
        string for the name of the field the act acts on rule (IP source, port range...)

    Attributes
    ----------
    start : int
    end : int
    max_card : int
    card : int
        cardinality of the rule
    empty_flag : int
        1 if the rule is empty, 0 otherwise
    field : str

    Examples
    --------
        >>> r1 = Range(1,7)
        >>> r2 = Range(0,4)
    """

    def __init__(self, start, end, max_card=float('inf'), field=None):
        super().__init__(max_card, field)
        self.start = start
        self.end = end
        if self.start is not None and self.start is not None:
            if self.start > self.end or (self.start > self.max_card - 1) or (self.end > self.max_card - 1):  # the highest address is max_card - 1
                raise ValueError("Incorrect range")
            else:
                self.empty_flag = 0
                self.card = self.end - self.start + 1

    def __repr__(self):
        return f'[{self.start}, {self.end}]' if not self.empty_flag else '∅'

    def __eq__(self, other):
        if self.start == other.start and self.end == other.end:
            return True
        return False

    def __hash__(self):
        return hash((self.start, self.end))

    def __and__(self, other):

        """
        Returns the result of set intersection

        Parameters
        ---------
        other : Range OR WildcardExpr
            Accepts any Range but only WildcardExpr if the expr is exaclty \*

        Returns
        -------
        Range

        Examples
        --------
            >>> r1 = Range(1,7)
            >>> r2 = Range(0,4)
            >>> r1 & r2
            [1, 4]

        """

        if self.empty_flag | other.empty_flag:  # one of the sets is empty
            return Range(None, None)
        if isinstance(other, WildcardExpr) and other.expr == '*':  # the other expression matches it all
            return self
        if other.start > self.end:  # starts too late
            return Range(None, None)
        if other.end < self.start:  # finishes too early
            return Range(None, None)
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        return Range(start, end)

    def __lt__(self, other):

        """
        Check if self is included in other (equality is accepted)

        Parameters
        ---------
        other : Range OR WildcardExpr = '*' (other WildcardExpr instances not allowed)

        Returns
        -------
        bool

        Examples
        --------
            >>> r1 = Range(1,7)
            >>> r2 = Range(2,4)
            >>> r2 < r1
            True
        """

        if other.empty_flag:  # nothing is included in the empty set
            return False

        if self.empty_flag: #empty set included in all sets
            return True

        if isinstance(other, WildcardExpr) and other.expr == '*':  # other accepts it all
            return True

        if other.start <= self.start and other.end >= self.end:
            return True

        return False

    def get_card(self):
        return self.card

    def is_member(self, point):
        return True if not self.empty_flag and self.start <= point <= self.end else False

    def union(self, other):

        """
        Returns the union of both rules if the result is continuous, None otherwise

        Parameters
        ----------
        other : Range

        Returns
        -------
        Range or None

        Examples
        --------
            >>> r1 = Range(1,7)
            >>> r2 = Range(8,10)
            >>> r1.union(r2)
            [1, 10]
            >>> r3 = Range(9, 10)
            >>> r1.union(r3) is None
            True

        """

        if other.start > self.end + 1:  # starts too late = there is a gap
            return None
        if other.end + 1 < self.start:  # finishes too early
            return None
        start = min(self.start, other.start)
        end = max(self.end, other.end)
        return Range(start, end)
