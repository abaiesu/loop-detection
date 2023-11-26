# -*- coding: utf-8 -*-
"""
Copyright Antonia Baies
baies.antonia@gmail.com

This file is part of Loop Detection.
"""

from loop_detection.algo.combination import Combination


def basic_add_rule(r, UC):
    """"
    Adds a rule to a set of uncovered combinations and updates the set following the basic algorithm

    Parameters
    ----------
    r : Rule
        rule to add
    UC : set
        current set of Combination instances

    Returns
    -------
    set
        new set of Combinations instances

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


def get_UC_basic(R):
    """"
    Returns the set of uncovered combinations using the basic algorithm (add_rule_basic)

    Parameters
    ----------
    R : array-like
        list/set of tuples : (str, Rule)

    Returns
    -------
    set
        set of Combination instances

    """

    UC = set()

    # sort R by decreasing cardinality to start by the base rule = H
    R = sorted(R, key=lambda rule: rule[1].get_card(), reverse=True)

    for r in R:
        UC = basic_add_rule(Combination(r[1], comp=[r[0]]), UC)
    return UC
