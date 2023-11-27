from loop_detection import MultiField, Range, WildcardExpr
import pytest


def test_is_member():
    mf = MultiField([Range(10, 20), Range(1, 1)])
    assert mf.is_member((15, 1)) is True
    assert mf.is_member((5, 2)) is False
    mf = MultiField([Range(10, 20), WildcardExpr("01*1")])
    assert mf.is_member((15, "0111")) is True
    assert mf.is_member((5, "0100")) is False


def test_inter():
    mf1 = MultiField([Range(10, 20), Range(1, 1)])
    mf2 = MultiField([Range(15, 25), Range(1, 1)])
    intersection = mf1 & mf2
    assert isinstance(intersection, MultiField) is True  # closure
    assert intersection.rules[0].start == 15
    assert intersection.rules[0].end == 20
    assert intersection.rules[1].start == 1
    assert intersection.rules[1].end == 1


def test_card():
    mf1 = MultiField([Range(10, 20), Range(1, 1)])
    assert mf1.get_card() == 11
    mf2 = MultiField([Range(15, 25), Range(None, None)])
    assert mf2.get_card() == 0
    mf3 = MultiField([WildcardExpr("01*1"), WildcardExpr("*11*")])
    assert mf3.get_card() == 8


def test_incl():
    mf1 = MultiField([Range(10, 20), Range(10, 30)])
    mf2 = MultiField([Range(15, 20), Range(10, 10)])
    assert (mf2 < mf1) is True
    assert (mf1 < mf2) is False
    assert (mf1 < mf1) is True
