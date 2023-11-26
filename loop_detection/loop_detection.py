import networkx as nx
from algo.uc_algo import get_UC


def get_rule_set(fw_tables):
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

    rule_set = {}
    for node, rules in fw_tables.items():
        for i, rule in enumerate(rules):
            rule_set[rule[0]] = (node, rule[1], rule[2], i)
    return rule_set


def get_aliases(rule_set):
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

    aliases = {}

    for key, value in rule_set.items():
        rule_value = value[1]
        if rule_value in aliases:
            aliases[rule_value].add(key)
        else:
            aliases[rule_value] = {key}

    return aliases


def cycles_detection(UC, rule_set, aliases, early_stop=False):
    """
    Detects cycles in the induced graph of the each uncovered combination

    Parameters
    ----------
    UC : set
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


def loop_detection(fw_tables, early_stop=False):
    """
    Detects loops in the network detected by the input forwarding table

    Parameters
    ----------
    fw_tables : dict
        keys = name of the node/router
        values = list of the rules present at the node
        the rules are in the following format : (name : str, rule : Rule, action = None or name of the destination)
    early_stop : bool, default = False
        whether you want to stop at the first cycle encountered (True) or you want all the cycles (False)

    Returns
    -------
    list
        the items of the list are tuples of the form (atom : Combination, list of cycles)
        the cycles are lists with all the nodes involved

        if early_stop == True, the returned value will be a list of length 1 with the first cycle encountered

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

    UC = get_UC(R_set)

    return cycles_detection(UC, rule_set, aliases, early_stop)
