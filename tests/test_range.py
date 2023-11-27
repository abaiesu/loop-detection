from loop_detection import WildcardExpr, Range
import pytest


def test_failure():
    with pytest.raises(ValueError):
        r1 = Range(2, 1)


def test_is_member():
    r1 = Range(10, 20)
    assert r1.is_member(15) is True
    assert r1.is_member(5) is False


def test_inter():
    r1 = Range(10, 20)
    r2 = Range(15, 25)
    inter = r1 & r2
    assert isinstance(inter, Range) is True  # closure
    assert inter.start == 15
    assert inter.end == 20
    r3 = Range(30, 40)
    r4 = WildcardExpr('*')
    assert (r2 & r3).empty_flag == 1  # emptiness
    assert (r1 & r4).empty_flag == 0  # non-emptiness


def test_card():
    r1 = Range(10, 20)
    r2 = Range(1, 1)
    r3 = Range(30, 40)
    assert r1.get_card() == 11
    assert r2.get_card() == 1
    assert (r2 & r3).get_card() == 0


def test_incl():
    r1 = Range(10, 20)
    r2 = Range(1, 1)
    r3 = Range(0, 40)
    assert (r1 < r2) == False
    assert (r2 < r3) == True
    assert (r3 < r3) == True
