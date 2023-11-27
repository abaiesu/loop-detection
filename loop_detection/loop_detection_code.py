import networkx as nx
import matplotlib.pyplot as plt

from loop_detection.algo.uc_algo import get_UC
from loop_detection.algo.combination import Combination
from loop_detection.set_rep.range import Range
from loop_detection.set_rep.wildcardexpr import WildcardExpr
from loop_detection.set_rep.multifield import MultiField
from typing import Dict, List, Tuple, Set, Union

NodeName = Union[int, str]
Action = Union[NodeName, None]
Rule = Union[Range, WildcardExpr, MultiField]


def check_same_type(collection: List) -> bool:
    """Checks if all the elements in the iterable are of the same type.
    In the case of Multifield rules, it checks that each corresponding field has the same type """

    first_type = type(next(iter(collection), None))  # get the type of the first element in the collection
    same_types = all(isinstance(element, first_type) for element in collection)
    if not same_types:
        return False
    if first_type != MultiField:
        return True
    else:  # for multifields, check that all the fields are of the same type
        for field in range(len(collection[0].rules)):  # for each field
            fields_list = []
            for rule in collection:
                rules_list = rule.rules
                fields_list.append(rules_list[field])
            if not check_same_type(fields_list):
                return False
        return True


def get_rule_set(fw_tables: Dict[NodeName, List[Tuple[str, Rule, Action]]]) -> Dict[str, Tuple[NodeName, Rule, Action]]:
    """
    Merges all the rules from the forwarding table into the same set

    Parameters
    ----------
    fw_tables : dict
        keys = name of the node/router
        values = list of the rules present at the node
        the rules are in the following format : (name : str, rule : Rule, action = None or name of the destination)

    Returns
    -------
    dict
        the keys are the rule names : str, and the values are tuples of the form (start, value : Rule, action)

    """

    rule_set: Dict[str, Tuple[NodeName, Rule, Action]] = {}
    for node, rules in fw_tables.items():
        for rule in rules:
            if rule[0] in rule_set.keys():  # the name of the rule already exists in the rule set
                raise ValueError(f"The rule {rule[0]} already exists in node {rule_set[rule[0]][0]}")
            rule_set[rule[0]] = (node, rule[1], rule[2])
    return rule_set


def get_aliases(rule_set: Dict[str, Tuple[str, Rule, Action]]) -> Dict[Rule, Set[str]]:
    """
    Gets the dict of all names of a given rule

    Parameters
    ----------
    rule_set : set
        matches the output of get_rule_set

    Returns
    -------
    set
        dictionary where the keys are rule values, and the values are sets of valid names : str
    """

    aliases: Dict[Rule, Set[str]] = {}

    for key, value in rule_set.items():
        rule_value = value[1]
        if rule_value in aliases:
            aliases[rule_value].add(key)
        else:
            aliases[rule_value] = {key}

    return aliases


def cycles_detection(UC: Set[Combination],
                     rule_set: Dict[str, Tuple[NodeName, Rule, Action]],
                     aliases: Dict[Rule, Set[str]],
                     early_stop: bool = False) -> List[Tuple[Combination, List[List[NodeName]]]]:
    """
    Detects cycles in the induced graph of each uncovered combination

    Parameters
    ----------
    UC : set[Combinations]
        set of all uncovered combinations, matches the output of get_UC
    rule_set : set
        matches output of get_rule_set
    aliases : dict
        matches the output of get_aliases
    early_stop : bool, default = False
        whether you want to stop at the first cycle encountered (True) or you want all the cycles (False)

    Returns
    -------
    list
        the items of the list are tuples of the form (atom : Combination, list of cycles)
        the cycles are lists with all the nodes involved

        if early_stop == True, the returned value will be a list of length 1 with the first cycle encountered

    """

    loops = []

    for atom in UC:
        if len(atom.cont) == 2:  # less or equal 2 containers = H + optionally another rule NO LOOP !
            continue

        g = nx.MultiDiGraph()

        nodes = set()
        edges = set()
        for rule in atom.cont:
            names = aliases[rule.rule]  # get all the names of the rule
            for name in names:
                start = rule_set[name][0]  # for each name, get the orgin node
                end = rule_set[name][2]  # the destination
                nodes.add(start)
                if end is not None:  # if not a drop
                    nodes.add(end)
                    edges.add((start, end))  # create the edge

        g.add_nodes_from(nodes)
        g.add_edges_from(edges)

        cycles = list(nx.simple_cycles(g))
        if cycles:
            if early_stop:
                return [(atom, cycles)]

            loops.append((atom, cycles))

    return loops


def loop_detection(fw_tables: Dict[NodeName, List[Tuple[str, Rule, Action]]], early_stop: bool = False) \
    -> List[Tuple[Combination, List[List[NodeName]]]]:
    """
    Detects loops in a network from its forwarding tables

    Parameters
    ----------
    fw_tables : dict
        the keys of the dictionary are the names of the nodes/routers

        the values are the list of the rules present at the key node

        the rules are in the following format : (name : str, rule : Rule, action = None or name of the destination node)
    early_stop : bool, default = False
        whether to stop at the first cycle encountered (True) or you want to wait for all the cycles (False)

    Returns
    -------
    list
        the items of the list are tuples of the form (atom : Combination, list of cycles)

        the cycles are lists with all the nodes involved

        if early_stop == True, the returned value will be a list of length 1 with the first cycle encountered

    Examples
    --------

    >>> example_tables = {i : [] for i in range(4)}
    >>> example_tables[0] = [('R1', Range(1,5), 1), ('R2', Range(1,4), 1), ('R3', Range(0,1), None), ('H0', Range(0,5), None)]
    >>> example_tables[1] =  [('R4', Range(2,4), 3), ('H1', Range(0,5), None)]
    >>> example_tables[2] = [('R5', Range(0, 4), 3), ('H2', Range(0,5), None)]
    >>> example_tables[3] =  [('R7', Range(2,3), 1), ('R6', Range(4, 5), None), ('H3', Range(0,5), None)]
    >>> len(loop_detection(example_tables)) > 0
    True
    """

    rule_set = get_rule_set(fw_tables)
    aliases = get_aliases(rule_set)

    R = [(key, values[1]) for key, values in rule_set.items()]

    # remove duplicate rules (= different name but same rule)
    unique_count = {key: 0 for key in aliases.keys()}
    R_set = set()
    for rule in R:
        if unique_count[rule[1]] == 0:
            R_set.add(rule)
            unique_count[rule[1]] += 1

    R_rules = [r[1] for r in R_set]  # get a list of the rules alone to check for types
    if not check_same_type(R_rules):
        raise ValueError("The rules of the network don't have the same type")

    UC = get_UC(R_set)

    return cycles_detection(UC, rule_set, aliases, early_stop)
