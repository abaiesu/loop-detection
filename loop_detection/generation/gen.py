from loop_detection import MultiField, Range, WildcardExpr
import matplotlib.pyplot as plt
import networkx as nx
import random
import numpy as np
from typing import Dict, List, Tuple, Set, Union

NodeName = Union[int, str]
Action = Union[NodeName, None]
Rule = Union[Range, WildcardExpr, MultiField]


def get_wc_range(start, prefix_len):
    """prefix len = number of bits from start to be matched"""

    start_bin = format(start, '032b')
    res = ''
    for i in range(len(start_bin)):
        if i >= prefix_len:
            res += '*'
        else:
            res += start_bin[i]
    return res


def get_range_from_wc(expr):
    start = ''
    end = ''
    for i in range(len(expr)):
        if expr[i] == '*':
            start += '0'
            end += '1'
        else:
            start += expr[i]
            end += expr[i]

    start_decimal = int(start, 2)
    end_decimal = int(end, 2)

    return start_decimal, end_decimal


def highest_set_bit_exponent(binary_string):
    index = binary_string.find('1')
    if index == -1:
        return 0

    exponent = len(binary_string) - 1 - index

    return exponent


def create_collection_rules(num_rules, num_fields_wc=2, num_fields_r=3,
                            min_range=0, max_range=2 ** 32 - 1, wc_len=32,
                            small_k=False, origin=None):
    """"
    Returns a list of random rules

    Parameters
    ----------
    num_rules : int
        number of rules in the set (MANDATORY)
    num_fields_wc : int, default = 2
        number of wildcard fields per rule
    num_fields_r : int, default = 3
        number of range fields per rule
    min_range : int, default = 0
        min start of the ranges
    max_range : int, default =  100
        max end of the ranges
    wc_len : int, default = 6
        number of bits/characters in a wildcard expression
    small_k : bool, default = False
        whether to keep a low overlapping degree or not
    origin : int | str | None, optional
        name of the node to be associated with the produced collection

    Returns
    -------
    list

    """

    R = []

    # build the whole space
    if num_fields_r == 1 and num_fields_wc == 0:
        H = Range(min_range, max_range)
    elif num_fields_r == 0 and num_fields_wc == 1:
        H = WildcardExpr('*' * wc_len)
    else:
        H = MultiField([Range(min_range, max_range) for _ in range(num_fields_r)]  # add all the range fields
                        + [WildcardExpr('*' * wc_len) for _ in range(num_fields_wc)])  # add all the wildcard fields

    H.name = 'H'
    R.append(H)

    for i in range(num_rules):
        multif = []
        for j in range(num_fields_r):  # create the range fields
            if small_k:
                if np.log2(max_range + 1) != int(np.log2(max_range + 1)):
                    raise ValueError("Make sure that max_range is of the form: 2**n - 1")
                val = random.randint(min_range, max_range)  # get 2 random ints
                l = highest_set_bit_exponent(format(val, f'0{wc_len}b'))
                prefix_len = random.randint(wc_len - l, wc_len)
                expr = get_wc_range(val, prefix_len)
                start, end = get_range_from_wc(expr)
                if end > max_range:
                    raise ValueError("end value exceeds max_range")
            else:
                val1 = random.randint(min_range, max_range)  # get 2 random ints
                val2 = random.randint(min_range, max_range)
                start = min(val1, val2)  # make the smaller one be the start
                end = max(val1, val2)  # make the bigger one be the end
            multif += [Range(start, end)]  # add the range
        for k in range(num_fields_wc):  # add the wildcard fields
            s = ''
            for _ in range(wc_len):
                s += random.choice(['*', '1', '0'])
            multif += [WildcardExpr(s)]
        if len(multif) == 1:
            rule = multif[0]
        else:
            rule = MultiField(multif)
        if origin:
            rule.name = f'R_{origin}_{i}'
        else:
            rule.name = f'R_{i}'
        R.append(rule)

    return R


def generate_fw_tables(nb_nodes, max_range=10, small_k=False, m=16, p_max=2 / 3):

    """Returns a random forwarding table with nb_nodes nodes"""

    fw_tables = {i: [] for i in range(nb_nodes)}

    for node in fw_tables.keys():

        nb_rules = random.randint(1, int(p_max * nb_nodes))
        R = create_collection_rules(nb_rules, num_fields_wc=0, num_fields_r=1,
                                    max_range=max_range, small_k=small_k, origin=node)
        R = list(set(R))
        # add the base rule (mandatory at each node)
        H = R[0]  # create_collection_rules always returns H at the start
        fw_tables[node].append((H, None))

        # add the rest of the rules
        for r in R[1:]:
            action = random.choice([i for i in range(nb_nodes) if i != node] + [None])
            r.name = r.name + str(node)
            fw_tables[node].append((r, action))

    return fw_tables


def print_from_fw_tables(fw_tables):

    """For visualization, prints the network from its forwarding tables"""

    G = nx.MultiDiGraph()

    nodes = set()
    edges = set()
    for node, values in fw_tables.items():
        start = node
        for rule in values:
            end = rule[1]
            nodes.add(start)
            if end is not None:  # if not a drop
                nodes.add(end)
                edges.add((start, end))  # create the edge

    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    plt.figure(figsize=(4, 2))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, font_weight='bold', node_size=300,
            node_color='skyblue', arrowsize=10, connectionstyle='arc3, rad = 0.1')
    plt.show()
