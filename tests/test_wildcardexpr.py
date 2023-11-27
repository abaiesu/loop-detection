from loop_detection import WildcardExpr
import pytest


def test_failure():
    with pytest.raises(ValueError):
        r1 = WildcardExpr(".0")
    with pytest.raises(ValueError):
        r2 = WildcardExpr("210a")


def test_is_member():
    r1 = WildcardExpr("01*1")
    r2 = WildcardExpr("*")
    assert r1.is_member("0111") == True
    assert r1.is_member("0100") == False
    assert (r2.is_member("000001") == True)


def test_inter():
    r1 = WildcardExpr("01*1")
    r2 = WildcardExpr("*101")
    inter = r1 & r2
    assert isinstance(inter, WildcardExpr) == True  # test closure
    assert inter.expr == "0101"
    r3 = WildcardExpr("*011")
    result = r1 & r3
    assert result.empty_flag == 1
    assert result.get_card() == 0
    assert (result.expr == "0101") == False


def test_card():
    r1 = WildcardExpr("01*1")
    r2 = WildcardExpr("*0**")
    assert r1.get_card() == 2
    assert r2.get_card() == 2 ** 3


def test_incl():
    r1 = WildcardExpr("01*1")
    r2 = WildcardExpr("*0**")
    r3 = WildcardExpr("*1**")
    assert (r1 < r2) == False
    assert (r1 < r3) == True
    assert (r1 < r1) == True
