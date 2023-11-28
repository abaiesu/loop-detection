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


def add_rule(r: Combination, UC: Set[Combination]) -> Set[Combination]:
    """"
    Adds a rule to a set of uncovered combinations and updates the set following the more efficient algorithm

    Parameters
    ----------
    r : Combination
        new rule to add, wrapped with the Combination attributes
    UC : set[Combinations]
        current set of uncovered combinations

    Returns
    -------
    set[Combination]
        new set of uncovered combinations
    """

    if len(UC) == 0:
        r.cont.add(r)
        UC.add(r)
        return UC

    ############################### PARENT COMPUTATION ##################################

    new = set()  # combinations c&r that aren't present in UC yet
    incl = set()  # all combinations included in r (= combinations that involve r)

    inter = {c for c in UC if
             (c & r).rule.empty_flag == 0}  # get all the combinations which intersect with the new rule
    inter_sorted = sorted(inter, key=lambda c: c.rule.get_card())  # sort by non-decreasing cardinality

    for c in inter_sorted:  # for each comb in inter, starting from the smallest
        cc = c & r  # get the intersection with r
        if cc not in incl:  # if cc not already in the combinations included in r
            if cc not in UC:
                UC.add(cc)
                new.add(cc)  # to keep track of the newly generated combinations
            else:
                for elem in UC:  # cc already in UC, retrieve the corresponding element
                    if elem == cc:
                        cc = elem
                        break
            cc.parent = c  # set the minimal parent
            incl.add(cc)

        else:  # cc already in present in incl, then the parent is the one set previously
            for elem in incl:  # retrieve the combinations from incl, the last set version
                if elem == cc:
                    cc = elem
                    break
            if not cc.parent < c:  # if the parent of cc is NOT included in c, then cc is covered
                cc.covered = True

    # remove the covered combinations from all lists
    incl = {c for c in incl if not c.covered}
    new = {c for c in new if not c.covered}
    UC = {c for c in UC if not c.covered}

    ################################# ATOM SIZE COMPUTATION ##################################

    incl_sorted = sorted(incl, key=lambda c: c.rule.get_card())
    for c in incl_sorted:  # for each combination that includes r
        if c.atsize > 0:
            if c in new and c.parent is not None:
                c.parent.atsize -= c.atsize
                c.sup = {c.parent}
                c.sup.update(c.parent.sup)  # update sup
                c.cont.update(c.parent.cont)  # update the cont : take the same container as the parent

            to_add = set([d & r for d in c.sup if
                          d & r in incl and d & r != c])  # add in sup the intersection bewteen r and the elements of sup other than c itself
            c.sup.update(to_add)
            c.cont.add(r)  # add r as a container for c
            for d in c.sup:  # warning : these elements aren't refered too in UC, so we must retrive the equal (not same) combi from new
                if d in new:
                    matching_elem = next((elem for elem in new if elem == d), None)
                    if matching_elem:
                        matching_elem.atsize -= c.atsize  # update the size in UC

    UC = {uc for uc in UC if uc.atsize != 0}  # remove all covered combinations

    return UC


def get_UC(R: Iterable[Tuple[str, Rule]]) -> Set[Combination]:
    """
    Returns the set of uncovered combinations associated to the set of rules given as input

    Parameters
    ----------
    R : array-like
        list/set of tuples of the form : (name of the rules, rule)

    Returns
    -------
    set[Combination]

    Examples
    --------
        >>> r1 = Range(0, 4)
        >>> r2 = Range(1, 5)
        >>> h = Range(0, 7)
        >>> rules = [('h', h), ('r1',r1), ('r2', r2)]
        >>> get_UC(rules)
        {[0, 7], [0, 4], [1, 4], [1, 5]}
        >>> [uc.get_name() for uc in get_UC(rules)]
        ['h', 'h & r1', 'h & r1 & r2', 'h & r2']

    """

    UC: Set[Combination] = set()

    # sort R by decreasing cardinality to start by the base rule = H
    R = sorted(R, key=lambda rule: rule[1].get_card(), reverse=True)

    for r in R:
        UC = add_rule(Combination(r[1], comp=[r[0]]), UC)
    return UC
