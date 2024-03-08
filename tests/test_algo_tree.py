import numpy as np
from loop_detection.generation.gen import create_collection_rules
from loop_detection.loop_detection_code import reformat_R
import time
from loop_detection import get_UC, MultiField, WildcardExpr, Range
from typing import Iterable
from loop_detection.algo.uc_algo_no_tree import get_UC as get_UC_no_tree



def brute_vs_tree(num_fields_wc, num_fields_r, start, end, step,
                  wc_len = 32, max_range = 2 ** 32 - 1,
                  check_output=False, check_imp=False, small_k=True):

    for n in range(start, end, step):

        nb_tries = 3
        dur_brute_l = np.zeros(nb_tries)
        dur_tree_l = np.zeros(nb_tries)

        for i in range(nb_tries):

            R = create_collection_rules(n, num_fields_wc=num_fields_wc,
                                        num_fields_r=num_fields_r,  # 1
                                        max_range=max_range,
                                        wc_len=wc_len,
                                        small_k=small_k)

            R = reformat_R(R)

            # check the brute version
            start_time = time.time()
            UC = get_UC_no_tree(R)
            end_time = time.time()
            d_brute = end_time - start_time
            dur_brute_l[i] = d_brute

            # check the tree version
            start_time = time.time()
            UC_tree = get_UC(R)
            end_time = time.time()
            d_tree = end_time - start_time
            dur_tree_l[i] = d_tree

            if check_output:
                if UC != UC_tree:
                    return False


        dur_brute = np.mean(dur_brute_l)
        dur_tree = np.mean(dur_tree_l)

        if check_imp:
            print('n=', n, ', dur brute =', round(dur_brute, 2), 'sec , dur tree =', round(dur_tree, 2),
                'sec   ==> get_UC_tree is', round(dur_brute / dur_tree, 2), 'times faster')

    if check_output:
        print('ok')

    return True


def test():
    # 1D RANGES
    assert brute_vs_tree(num_fields_wc=0, num_fields_r=1, start=100, end=500, step=100, check_output=True)
    # 4D RANGES
    assert brute_vs_tree(num_fields_wc=0, num_fields_r=4, start=100, end=500, step=100, check_output=True)
    # 1D WC
    assert brute_vs_tree(num_fields_wc=1, num_fields_r=0, start=100, end=500, step=100, check_output=True)
    # 4D WC
    assert brute_vs_tree(num_fields_wc=4, num_fields_r=0, start=100, end=500, step=100, check_output=True)
    # 3D RANGES + 2D WC
    assert brute_vs_tree(num_fields_wc=2, num_fields_r=3, start=100, end=500, step=100, check_output=True)
    # small k
    assert brute_vs_tree(num_fields_wc=0, num_fields_r=1, start=1, end=10, step=1, check_output=True, small_k=False)

