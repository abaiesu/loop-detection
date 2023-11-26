from loop_detection.algo.combination import Combination
from loop_detection.algo.basic_uc_algo import get_UC_basic
from loop_detection import Range, MultiField, get_UC
from tests.random_generation import create_collection_rules
import random

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


################### PAPER EXAMPLE 1D ##################

def test1():
    r1 = Range(0, 4)
    r2 = Range(1, 5)
    r3 = Range(2, 6)
    r4 = Range(3, 3)
    h = Range(0, 7)

    r = [('h', h), ('r1', r1), ('r2', r2), ('r3', r3), ('r4', r4)]

    UC_n = get_UC_naive(r)
    UC_alg = get_UC(r)
    UC_b = get_UC_basic(r)
    assert set(UC_n) == set(UC_alg)
    assert set(UC_n) == set(UC_b)


############# TEST ON RANDOM RULES 1D #################

def test2():
    for _ in range(10):
        n = random.randint(5, 15)
        R = create_collection_rules(n, num_fields_wc=0, num_fields_r=1, max_range=20)
        UC_alg = get_UC(R)
        UC_b = get_UC_basic(R)
        UC_n = get_UC_naive(R)
        assert set(UC_n) == set(UC_alg)
        assert set(UC_n) == set(UC_b)


################ PAPER EXAMPLE 2D #####################

def test3():

    R = [('R1', MultiField([Range(0, 5), Range(5, 8)])),  # R1
         ('R2', MultiField([Range(3, 10), Range(5, 8)])),  # R2
         ('R3', MultiField([Range(3, 5), Range(0, 6)])),  # R3
         ('R4', MultiField([Range(3, 8), Range(7, 9)]))  # R4
         ]

    H = MultiField([Range(0, 10), Range(0, 9)])

    R = [('H', H)] + R

    UC_alg = get_UC(R)
    UC_b = get_UC_basic(R)
    assert set(UC_b) == set(UC_alg)


################ RANGES + WILDCARDs TESTS ##############

def test4():

    for _ in range(10):
        n = random.randint(5, 20)
        R = create_collection_rules(n, num_fields_wc=2, num_fields_r=3)
        UC_alg = get_UC(R)
        UC_b = get_UC_basic(R)
        assert set(UC_b) == set(UC_alg)
