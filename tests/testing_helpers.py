from loop_detection import MultiField, Range, WildcardExpr
import matplotlib.pyplot as plt
import networkx as nx
import random
from loop_detection.algo.combination import Combination


def create_collection_rules(num_rules, num_fields_wc=2, num_fields_r=3, min_range=0, max_range=100, wc_len=6):
    """"
    Returns a list of random rules

    Parameters
    ----------
    num_rules : int
        number of rules in the set
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


    Returns
    -------
    list
        list of tuples of the form (str, Rule), where str is the name of the rule

    """

    R = []

    # build the whole space
    H = MultiField([Range(min_range, max_range) for _ in range(num_fields_r)]  # add all the range fields
                   + [WildcardExpr('*' * wc_len) for _ in range(num_fields_wc)])  # add all the wildcard fields

    if len(H.rules) == 1:
        H = H.rules[0]

    R.append(('H', H))

    for i in range(num_rules):
        multif = []
        for j in range(num_fields_r):  # create the range fields
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
        R.append((f'R{i}', rule))

    return R


def generate_fw_tables(nb_nodes, max_range=10):
    """Returns a random forwarding table with nb_nodes nodes"""

    fw_tables = {i: [] for i in range(nb_nodes)}

    for node in fw_tables.keys():

        nb_rules = random.randint(1, int((2 / 3) * nb_nodes))
        R = create_collection_rules(nb_rules, num_fields_wc=0, num_fields_r=1, max_range=max_range)

        # add the base rule (mandatory at each node)
        H = R[0]  # create_collection_rules always returns H at the start
        if random.random() < 0.8:  # 80% : H -> drop
            fw_tables[node].append((f'H{node}', H[1], None))
        else:  # 20% : H -> node
            action = random.choice([i for i in range(nb_nodes) if i != node])
            fw_tables[node].append((f'H{node}', H[1], action))

        # add the rest of the rules
        for r in R[1:]:
            action = random.choice([i for i in range(nb_nodes) if i != node] + [None])
            fw_tables[node].append((r[0] + str(node), r[1], action))

    return fw_tables


def print_from_fw_tables(fw_tables):
    """For visualization, prints the network from its forwarding tables"""

    G = nx.MultiDiGraph()

    nodes = set()
    edges = set()
    for node, values in fw_tables.items():
        start = node
        for rule in values:
            end = rule[2]
            nodes.add(start)
            if end is not None:  # if not a drop
                nodes.add(end)
                edges.add((start, end))  # create the edge

    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    plt.figure(figsize=(4, 2))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, font_weight='bold', node_size=300, node_color='skyblue', arrowsize=10)
    plt.show()


############# NAIVE IMPLEMENTATION IN 1D ##############

def get_UC_naive(R):
    R = [Combination(r[1], comp=[r[0]]) for r in R]

    ##################### GET ALL COMBINATIONS (INCREMENTALLY) ###################

    all_combinations = []
    for r in R:
        new = []
        if len(all_combinations) == 0:
            all_combinations.append(r)
        else:
            for comb in all_combinations:
                if (comb & r).rule.empty_flag != 1:
                    new.append(comb & r)
            all_combinations += new

    all_combinations = list(set(all_combinations))  # remove duplicates

    ######################## GET THE UNCOVERED COMBINATIONS ######################

    UC = []

    if isinstance(all_combinations[0].rule, Range):
        Rr = [r.rule for r in R]  # extract all the rules (R is made out of combinations)
        for comb in all_combinations:
            if is_covered_r(comb.rule, Rr) == False:
                UC.append(comb)

    else:
        print("This data type isn't supported", all_combinations[0].rule.__class__.__name__)

    return UC


def is_covered_r(comb, R):
    non_containers = get_non_containers(comb, R)
    # keep only the non-containers which can cover comb (= which intersect with it)
    non_containers = [nc for nc in non_containers if (nc & comb).empty_flag != 1]
    if len(non_containers) == 0:  # there are no non-containers, so there is nothing to check
        return False
    else:
        # sort from the earliest start
        non_containers = sorted(non_containers, key=lambda x: x.start)
        u = non_containers[0]
        for nc in non_containers:  # get the union of the relevant non-containers
            u = u.union(nc)
            if u is None:  # if the union is disjoint, there is a hole which isn't covered
                return False
        if u is not None and (
            not comb < u):  # if the union is continuous AND comb isn't covered by U, then comb is uncovered
            return False
        return True


def get_non_containers(c, R):
    res = []
    for r in R:
        if not c < r:
            res.append(r)
    return res
