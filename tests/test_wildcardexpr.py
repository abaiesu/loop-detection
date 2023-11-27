from loop_detection import WildcardExpr
import pytest


def test_failure():
    with pytest.raises(ValueError):
        r1 = WildcardExpr(".0")
    with pytest.raises(ValueError):
        r2 = WildcardExpr("210a")
    with pytest.raises(ValueError):
        r3 = WildcardExpr("1****", max_card=2**3)


def test_is_member():
    r1 = WildcardExpr("01*1")
    r2 = WildcardExpr("*")
    assert r1.is_member("0111") == True
    assert r1.is_member("0100") == False
    assert (r2.is_member("000001") == True)
    r6 = WildcardExpr("01")
    r7 = WildcardExpr("10")
    r8 = r6 & r7
    assert r8.is_member("10") == False
    assert r7.is_member("10001") == False


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
    r4 = WildcardExpr("*")
    r5 = WildcardExpr("*01")
    assert (r4 & r5) == r5
    with pytest.raises(ValueError):
        r6 = r5 & r3
    r6 = WildcardExpr("01")
    r7 = WildcardExpr("10")
    r8 = r6 & r7
    assert r8.empty_flag == 1
    assert (r6 & r8).empty_flag == 1


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
