from loop_detection.classes import Combination
from loop_detection import Range

def get_UC_naive(R):
    R = [Combination(r, comp={r.name}) for r in R]

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
