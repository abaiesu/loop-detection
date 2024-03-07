from loop_detection.classes import Range, WildcardExpr, Combination, MultiField, Trie, Node, build_interval_tree
from typing import Set, Union, Iterable

NodeName = Union[int, str]
Action = Union[NodeName, None]
Rule = Union[Range, WildcardExpr, MultiField]


def common_elements(list_of_sets: Iterable[Set]) -> Set[Rule]:

    """" Returns the set of elements present in all the sets provided as input"""

    if not list_of_sets:
        return set()

    common_set = set(list_of_sets[0])

    for s in list_of_sets[1:]:
        common_set = common_set.intersection(s)

    return common_set


def get_intersections(trees: Iterable[Node], r: Rule) -> Set[Rule]:

    """" Returns a set of rules which intersect with the query rules r"""

    result = []
    for tree in trees:
        inters = tree.find_intersects(r)
        result.append(inters)
    ret = common_elements(result)
    return ret

def add_rule(r, UC, trees):
    """"
    Adds a rule to a set of uncovered combinations and updates the set following the more efficient algorithm

    Parameters
    ----------
    r : Rule
        new rule to add
    UC : set
        current set of Combination instances
    trees : list
        list of the trees for each dimension (trie, interval trees)

    Returns
    -------
    set
        new set of Combination instances
    """

    if len(UC) == 0:
        #r.cont.add(r)
        r.cont.append(r)
        UC.add(r)
        for tree in trees:
            tree.add_to_tree(r)
        return UC#, trees

    ############################### PARENT COMPUTATION ##################################

    new = set()  # combinations c&r that aren't present in UC yet
    incl = set()  # all combinations that include r

    if len(trees) == 1:
        inter = trees[0].find_intersects(r)  # only a range or only a wildcard
    else:
        inter = get_intersections(trees, r)  # a multifield : we must go through each dimension


    inter = sorted(inter, key=lambda c: c.rule.get_card())  # sort by non-decreasing cardinality

    for c in inter:  # for each comb in inter, starting from the smallest
        cc = c & r  # get the intersection with r
        if cc not in incl:  # if cc not already in the combis included in r
            if cc not in UC:
                UC.add(cc)
                new.add(cc)  # to keep track of the newly generated combis
            else:
                for elem in UC:  # cc already in UC, retreive the corresonding element
                    if elem == cc:
                        cc = elem
                        break
            cc.parent = c  # set the minimal parent
            incl.add(cc)

        else:  # cc already in present in incl, then the parent is the one set previously
            for elem in incl:  # retreive the combi from incl, the last set version
                if elem == cc:
                    cc = elem
                    break
            if not cc.parent < c:  # if the parent of cc is NOT included in c, then cc is covered
                cc.covered = True

    # remove the covered combis from all lists
    incl = {c for c in incl if not c.covered}
    new = {c for c in new if not c.covered}
    UC = {c for c in UC if not c.covered}

    for uc in new:
        for tree in trees:
            tree.add_to_tree(uc)

    ################################# ATOM SIZE COMPUTATION ##################################

    incl = sorted(incl, key=lambda c: c.rule.get_card())
    for c in incl:  # for each combination that include r
        if c.atsize > 0:
            if c in new:
                c.parent.atsize -= c.atsize
                c.sup = {c.parent}
                c.sup.update(c.parent.sup)  # update sup
                #c.cont.update(c.parent.cont)  # update the cont : take the same container as the parent
                c.cont += c.parent.cont

            intersections = {d & r for d in c.sup}
            to_add = {intersection for intersection in intersections - {c} if
                      intersection in incl}  # add in sup the intersection bewteen r and the elements of sup other than c itself
            c.sup.update(to_add)

            #if len(r.comp) != 1: #we add a combination from a previous get_UC computation (valid when propagation is used)
                #c.cont = c.cont | r.cont
            #    c.cont += r.cont
            #else:
            #    #c.cont.add(r)  # add r as a container for c
            c.cont.append(r)
            for d in c.sup:  # warning : these elements aren't refered too in UC, so we must retrive the equal (not same) combi from new
                if d in new:
                    matching_elem = next((elem for elem in new if elem == d), None)
                    if matching_elem:
                        matching_elem.atsize -= c.atsize  # update the size in UC

    for uc in UC.copy():
        if uc.atsize == 0:
            #print("remove", uc.get_name(), uc)
            UC.remove(uc)
            #print('after removing', [(u, u.get_name()) for u in UC])
            for tree in trees:
                #print("at size empty", uc.get_name(), uc)
                tree.remove_from_tree(uc)

    #print('before return', [i.get_name() for i in UC])

    return UC#, trees


def get_UC(R):
    """"
    Returns the set of uncovered combinations using the algorithm with the best complexity (add_rule)

    Parameters
    ----------
    R : iterable
        list/set Rules

    Returns
    -------
    set
        set of Combination instances

    """

    UC = set()

    max_rule = max(R, key=lambda rule: rule.get_card())
    R.remove(max_rule)
    R.insert(0, max_rule)

    # create the skeleton of the trees, but don't add elements yet

    if isinstance(R[0], Range): # range : one interval tree for the whole collection
        trees = [build_interval_tree(R, keep_empty=True)]

    elif isinstance(R[0], WildcardExpr): # wc : one trie for the whole collection
        wc_len = len(R[0].expr)
        trees = [Trie(key=None, depth=0, l=wc_len + 1)]

    elif isinstance(R[0], MultiField):  # multifield : one trie and multiple interval trees
        num_r = 0
        num_wc = 0
        wc_len = 0
        for rule in R[0].rules:
            if isinstance(rule, Range):
                num_r += 1
            else:
                num_wc += 1
                wc_len = len(rule.expr)

        trees = [build_interval_tree(R, keep_empty=True, axis=i) for i in range(num_r)]
        if num_wc == 1:
            trees.append(Trie(key=None, depth=0, l=wc_len + 1))

    else:
        raise ValueError('Invalid Class ', type(R[0]))

    for i, r in enumerate(R):
        UC = add_rule(Combination(r, comp={r.name}), UC, trees)

    return UC
