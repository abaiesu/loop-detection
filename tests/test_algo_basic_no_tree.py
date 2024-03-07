from loop_detection.algo.basic_uc_algo import get_UC_basic
from loop_detection.algo.uc_algo_no_tree import get_UC as get_UC_no_tree
from loop_detection import Range, MultiField, get_UC
from loop_detection.generation.gen import create_collection_rules
from tests.testing_helpers import get_UC_naive
import random
import pytest


################### PAPER EXAMPLE 1D ##################

@pytest.fixture
def one_d_example():
    r1 = Range(0, 4, 'r1')
    r2 = Range(1, 5, 'r2')
    r3 = Range(2, 6, 'r3')
    r4 = Range(3, 3, 'r4')
    h = Range(0, 7, 'h')

    return [h, r1, r2, r3, r4]


def test_one_d_example_basic(one_d_example):
    UC_n = get_UC_naive(one_d_example)
    UC_b = get_UC_basic(one_d_example)
    assert set(UC_n) == set(UC_b)


def test_one_d_example_algo(one_d_example):
    UC_n = get_UC_naive(one_d_example)
    UC_algo = get_UC_no_tree(one_d_example)
    assert set(UC_n) == set(UC_algo)


############# TEST ON RANDOM RULES 1D ################

@pytest.fixture
def one_d_random():
    n = random.randint(5, 15)
    R = create_collection_rules(n, num_fields_wc=0, num_fields_r=1, max_range=20, small_k=False)
    return R


def test_one_d_rand1_basic(one_d_random):
    UC_b = get_UC_basic(one_d_random)
    UC_n = get_UC_naive(one_d_random)
    assert set(UC_n) == set(UC_b)


def test_one_d_rand1_algo(one_d_random):
    UC_algo = get_UC_no_tree(one_d_random)
    UC_n = get_UC_naive(one_d_random)
    assert set(UC_n) == set(UC_algo)


def test_one_d_rand2_basic(one_d_random):
    UC_b = get_UC_basic(one_d_random)
    UC_n = get_UC_naive(one_d_random)
    assert set(UC_n) == set(UC_b)


def test_one_d_rand2_algo(one_d_random):
    UC_algo = get_UC_no_tree(one_d_random)
    UC_n = get_UC_naive(one_d_random)
    assert set(UC_n) == set(UC_algo)


################ PAPER EXAMPLE 2D #####################

@pytest.fixture
def two_d_example():
    R = [MultiField([Range(0, 5), Range(5, 8)], 'R1'),  # R1
         MultiField([Range(3, 10), Range(5, 8)],  'R2'),  # R2
         MultiField([Range(3, 5), Range(0, 6)],'R3'),  # R3
         MultiField([Range(3, 8), Range(7, 9)], 'R4')  # R4
         ]

    H = MultiField([Range(0, 10), Range(0, 9)], 'H')

    R = [H] + R

    return R


def test_two_d_example(two_d_example):
    UC_b = get_UC_basic(two_d_example)
    UC_algo = get_UC_no_tree(two_d_example)
    assert set(UC_b) == set(UC_algo)


################ RANGES + WILDCARDS TESTS ##############

@pytest.fixture
def five_d_random():
    n = random.randint(5, 20)
    R = create_collection_rules(n, num_fields_wc=2, num_fields_r=3)
    return R


def test_five_d_rand1(five_d_random):
    UC_b = get_UC_basic(five_d_random)
    UC_algo = get_UC(five_d_random)
    assert set(UC_b) == set(UC_algo)


def test_five_d_rand2(five_d_random):
    UC_b = get_UC_basic(five_d_random)
    UC_algo = get_UC(five_d_random)
    assert set(UC_b) == set(UC_algo)


def test_five_d_rand3(five_d_random):
    UC_b = get_UC_basic(five_d_random)
    UC_algo = get_UC(five_d_random)
    assert set(UC_b) == set(UC_algo)
