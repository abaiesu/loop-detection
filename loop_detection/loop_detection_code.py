# -*- coding: utf-8 -*-
"""
Copyright Antonia Baies
baies.antonia@gmail.com

This file is part of Loop Detection.
"""

import networkx as nx
from loop_detection.classes import Range, WildcardExpr, Combination, MultiField
from loop_detection.algo.uc_algo import get_UC
from typing import Dict, List, Tuple, Set, Union, Iterable

NodeName = Union[int, str]
Action = Union[NodeName, None]
Rule = Union[Range, WildcardExpr, MultiField]


def check_same_type(collection: List) -> bool:
    """
    Checks if all the elements in the iterable are of the same type.
    In the case of Multifield rules, it checks that each corresponding field has the same type

     >>> R = [Range(0, 1), Range(4, 9), WildcardExpr('**1')]
     >>> check_same_type(R)
     False
     >>> R = [MultiField([Range(0, 1), Range(4, 9)]), MultiField([WildcardExpr('**1'), Range(7, 10)])]
     >>> check_same_type(R)
     False
     >>> R = [MultiField([Range(0, 1), Range(4, 9)]), MultiField([Range(7, 10), Range(9, 10), Range(5, 5)])]
     >>> check_same_type(R)
     False
     >>> R = [Range(0, 1), Range(4, 9)]
     >>> check_same_type(R)
     True

     """

    first_type = type(next(iter(collection), None))  # get the type of the first element in the collection
    same_types = all(isinstance(element, first_type) for element in collection)
    if not same_types:
        return False
    if first_type != MultiField:
        return True
    else:  # for multifields, check that all the fields are of the same type
        nb_inner_rules = len(collection[0].rules)  # first check that they have the same number of fields
        for mf in collection:
            if len(mf.rules) != nb_inner_rules:
                return False
        for field in range(len(collection[0].rules)):  # for each field
            fields_list = []
            for rule in collection:
                rules_list = rule.rules
                fields_list.append(rules_list[field])
            if not check_same_type(fields_list):
                return False
        return True


def reformat_R(R: List[Rule]) -> List[Rule]:
    """If the ruleset is made out of Multifields, we merge all the wildcard expressions into one
    First the range rules, then the unique wildcard expression

    >>> R = [MultiField([WildcardExpr('***'), WildcardExpr('*11'), Range(6, 10)])]
    >>> RR = reformat_R(R)
    >>> RR[0] == MultiField([Range(6, 10), WildcardExpr('****11')])
    True
    """

    if isinstance(R[0], MultiField):  # we assume that all the rules are of the same type
        num_r = 0
        num_wc = 0
        for rule in R[0].rules:  # count the number of range rule and wc rules
            if isinstance(rule, Range):
                num_r += 1
            else:
                num_wc += 1

        if num_wc > 1:  # if there are more than 1 wc rules
            RR: List[Rule] = []
            for r in R:
                res_wc = ''  # store all the wc rules
                range_rules = []  # store all the range rules
                if isinstance(r, MultiField):
                    for rule in r.rules:
                        if isinstance(rule, Range):
                            range_rules.append(rule)
                        else:
                            res_wc += rule.expr
                    RR.append(MultiField(range_rules + [WildcardExpr(res_wc)], r.name))
                else:
                    raise ValueError("All the rules from the collection must be of the same type")
            return RR

        return R

    else:
        return R


def get_rule_dict(fw_tables: Dict[NodeName, List[Tuple[Rule, Action]]]) -> Dict[str, Tuple[NodeName, Rule, Action]]:

    """Merges all the tables into a dictionary with the name of the rule and (source, rule, action)"""

    rule_dict = {}
    for node, rules in fw_tables.items():
        for i, rule in enumerate(rules):
            rule_dict[rule[0].name] = (node, rule[0], rule[1])

    return rule_dict


def get_R_per_subgraph(fw_tables: Dict[NodeName, List[Tuple[Rule, Action]]]):

    G = nx.MultiDiGraph()

    nodes = set()
    edges = set()

    dests_per_node = {}
    for node, rules in fw_tables.items():
        dests_per_node[node] = {rule[1] for rule in rules}  # keep track of the possible destinations

    for n, d in dests_per_node.items():
        nodes.add(n)
        for dd in d:
            if dd is not None:
                nodes.add(dd)
                edges.add((n, dd))

    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    connected_subgraphs = list(nx.strongly_connected_components(G))

    rule_sets = []
    for graph in connected_subgraphs:
        R = []
        for n in graph:
            R += fw_tables[n]
        R_clean = [r[0] for r in R]
        rule_sets.append(R_clean)

    return rule_sets


def cycle_detection(UC_to_test: Iterable[Combination], rule_set: Dict[str, Tuple[NodeName, Rule, Action]]) -> List[Tuple[Combination, List[NodeName]]]:

    """Creates from each UC in UC_to_test the forwarding graph of the UC and checks for cycles"""

    total_cycles = []

    for atom in UC_to_test:

        g = nx.MultiDiGraph()

        nodes = set()
        edges = set()

        for container in atom.cont:  # for each rule containing the atom
            name = container.get_name()
            start = rule_set[name][0]  # get the location
            end = rule_set[name][2]  # get the action
            nodes.add(start)
            if end is not None:  # if not a drop
                nodes.add(end)
                edges.add((start, end))  # create the edge

        g.add_nodes_from(nodes)
        g.add_edges_from(edges)

        cycles = list(nx.simple_cycles(g))
        if cycles:
            total_cycles.append((atom, cycles))

    return total_cycles


def loop_detection(fw_tables: Dict[NodeName, List[Tuple[Rule, Action]]], merge: bool=False) -> List[Tuple[Combination, List[NodeName]]]:

    """
    Returns a list with tuples (atom, cycles) with the cycles induced by each atom

    Parameters
    ----------
    fw_tables : Dict[NodeName, List[Tuple[Rule, Action]]]
        dictionary that associates each node with its set of (rule, action) tuples
    merge : Bool, default = False
        whether to merge the rules of the whole network or to only merge within strongly connected nodes

    Returns
    -------
    List[Tuple[Combination, List[NodeName]]]
        cycles in the network, with the atom that induced them
    """

    # first check that the fw_tables are well-formed
    R = []
    for node, rules in fw_tables.items():
        for r in rules:
            R.append(r[0])
    if not check_same_type(R):
        raise ValueError("The rules don't all have the same format")

    # reformat each rule
    Rs: List[List[Rule]] = []
    dests = []
    nodes = []
    for node, rules in fw_tables.items():
        nodes.append(node)
        des = []
        R = []
        for r in rules:
            des.append(r[1])
            R.append(r[0])
        RR: List[Rule] = reformat_R(R)
        Rs.append(RR)
        dests.append(des)

    fw_tables_reformatted: Dict[NodeName, List[Tuple[Rule, Action]]] = {}
    for n, d, r in zip(nodes, dests, Rs):
        for rr, dd in zip(r, d):
            to_add: Tuple[Rule, Action] = (rr, dd)
            if n in fw_tables_reformatted.keys():
                fw_tables_reformatted[n].append(to_add)
            else:
                fw_tables_reformatted[n] = [to_add]

    # run the loop detection
    rule_set = get_rule_dict(fw_tables)

    if not merge:
        cycles = []
        Rs = get_R_per_subgraph(fw_tables)
        for R in Rs:
            UC = get_UC(R)
            cycles += cycle_detection(UC, rule_set)
        return cycles

    else:
        R = [r[1] for r in rule_set.values()]
        UC = get_UC(R)
        return cycle_detection(UC, rule_set)




