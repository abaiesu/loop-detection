# -*- coding: utf-8 -*-
"""
Copyright Antonia Baies
baies.antonia@gmail.com

This file is part of Loop Detection.
"""

from loop_detection.algo.combination import Combination
from loop_detection.set_rep.range import Range
from loop_detection.set_rep.wildcardexpr import WildcardExpr
from loop_detection.set_rep.multifield import MultiField
from typing import Set, Union, Iterable, Tuple

NodeName = Union[int, str]
Action = Union[NodeName, None]
Rule = Union[Range, WildcardExpr, MultiField]


def basic_add_rule(r: Combination, UC: Set[Combination]):
    """
    Adds a rule to a set of uncovered combinations and updates the set following the basic algorithm

    Parameters
    ----------
    r : Combination
        new rule to add, wrapped with the Combination attributes
    UC : set[Combinations]
        current set of uncovered combinations

    Returns
    -------
    set[Combination]

    """

    if len(UC) == 0:
        UC.add(r)
        return UC

    new = {c & r for c in UC if (c & r).rule.empty_flag != 1}
    UC.update(new)

    for c in UC:
        c.atsize = c.rule.get_card()
        c.sup = {d for d in UC if c < d and c != d}
    UC = sorted(UC, key=lambda c: c.rule.get_card())
    for c in UC:
        for d in c.sup:
            d.atsize -= c.atsize

    UC = {uc for uc in UC if uc.atsize != 0}

    return UC


def get_UC_basic(R: Iterable[Tuple[str, Rule]]) -> Set[Combination]:
    """"
    Returns the set of uncovered combinations using the basic algorithm (add_rule_basic)

    Parameters
    ----------
    R : array-like
        list/set of tuples : (str, Rule)

    Returns
    -------
    set[Combination]

    """

    UC: Set[Combination] = set()  # this will sort the uncovered combinations

    # sort R by decreasing cardinality to start by the base rule = H
    R = sorted(R, key=lambda rule: rule[1].get_card(), reverse=True)

    for r in R:
        UC = basic_add_rule(Combination(r[1], comp=[r[0]]), UC)
    return UC
