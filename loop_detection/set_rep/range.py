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

    Attributes
    ----------
    pair : tuple
        format = (start, end)
        start and end are both included
        valid example : (5, 7)
        invalid example : (7, 5)
    max_card : int, default = infinity
    field : None

    Examples
    --------
        >>> r1 = Range((1,7))
        >>> r2 = Range((0,4))
        >>> Range((2, 4)) < r1
        True
        >>> r1.get_card()
        7
        >>> r3 = Range((8,9))
        >>> r1.union(r3)
        [1, 9]
        >>> r4 = Range((9, 10))
        >>> r1.union(r4) is None
        True

    """

    def __init__(self, pair, max_card=float('inf'), field=None):
        super().__init__(pair, max_card, field)
        if pair is not None:
            start, end = pair[0], pair[1]
            if start > end or end > max_card - 1:  # the highest address is max_card - 1
                raise ValueError("Incorrect range")
            self.start = start
            self.end = end
            self.card = self.end - self.start + 1 if not self.empty_flag else 0
        else:
            self.start = None
            self.end = None

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
        other : Range OR WildcardExpr = '*' (other WildcardExpr instances not allowed)

        Returns
        -------
        Range

        """

        if self.empty_flag | other.empty_flag:  # one of the sets is empty
            return Range(None)
        if isinstance(other, WildcardExpr) and other.expr == '*':  # the other expression matches it all
            return self
        if other.start > self.end:  # starts too late
            return Range(None)
        if other.end < self.start:  # finishes too early
            return Range(None)
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        return Range((start, end))

    def __lt__(self, other):

        """
        Check if self is included in other (equality is accepted)

        Parameters
        ---------
        other : Range OR WildcardExpr = '*' (other WildcardExpr instances not allowed)

        Returns
        -------
        bool
        """

        if other.empty_flag:  # nothing is included in the empty set
            return False

        if isinstance(other, WildcardExpr) and other.string == '*':  # other accepts it all
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

        """

        if other.start > self.end + 1:  # starts too late = there is a gap
            return None
        if other.end + 1 < self.start:  # finishes too early
            return None
        start = min(self.start, other.start)
        end = max(self.end, other.end)
        return Range((start, end))
