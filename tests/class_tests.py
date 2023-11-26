from loop_detection import WildcardExpr, Range, MultiField
import pytest


############################ TEST RANGE CLASS #################################

def test_range_operations():
    # test is_member
    r1 = Range(10, 20)
    assert r1.is_member(15) is True
    assert r1.is_member(5) is False

    # test inter
    r2 = Range(15, 25)
    inter = r1 & r2
    assert isinstance(inter, Range) is True  # closure
    assert inter.start == 15
    assert inter.end == 20
    r3 = Range(30, 40)
    assert (r2 & r3).empty_flag == 1  # emptiness
    r4 = WildcardExpr('*')
    assert (r1 & r4).empty_flag == 0  # non-emptiness

    # test card
    assert r1.get_card() == 11
    r5 = Range(1, 1)
    assert r5.get_card() == 1
    assert (r2 & r3).get_card() == 0

    # test inclusion
    assert r5 < r1 == False
    r6 = Range(0, 100)
    assert r5 < r6 == True
    assert r6 < r6 == True


############################ TEST WILDCARD CLASS #################################

def test_wildcard_operations():
    # test is_member
    expr = WildcardExpr("01*1")
    assert expr.is_member("0111") == True
    assert expr.is_member("0100") == False
    expr = WildcardExpr("*")
    assert expr.is_member("000001") == True

    # test inter
    expr1 = WildcardExpr("01*1")
    expr2 = WildcardExpr("*101")
    inter = expr1 & expr2
    assert isinstance(inter, WildcardExpr) == True  # test closure
    assert inter.expr == "0101"

    expr1 = WildcardExpr("01*1")
    expr2 = WildcardExpr("*011")
    result = expr1 & expr2
    assert result.empty_flag == 1
    assert result.get_card() == 0
    assert (result.expr == "0101") == False

    # test cardinality
    expr = WildcardExpr("01*1")
    assert expr.get_card() == 2
    expr = WildcardExpr("*1**")
    assert expr.get_card() == 2 ** 3

    # test inclusion
    assert expr1 < expr2 == False
    assert expr < expr1 == True


############################ TEST MULTIRANGE CLASS #################################

def test_multifield_operations():
    # test is_member
    rules1 = [Range(10, 20), Range(1, 1)]
    mr = MultiField(rules1)
    assert mr.is_member((15, 1)) is True
    assert mr.is_member((5, 2)) is False
    rules = [Range((10, 20)), WildcardExpr("01*1")]
    mr = MultiField(rules)
    assert mr.is_member((15, "0111")) is True
    assert mr.is_member((5, "0100")) is False

    # test inter
    rules2 = [Range(15, 25), Range(1, 1)]
    mr1 = MultiField(rules1)
    mr2 = MultiField(rules2)
    intersection = mr1 & mr2
    assert isinstance(intersection, MultiField) is True  # closure
    assert intersection.rules[0].start == 15
    assert intersection.rules[0].end == 20
    assert intersection.rules[1].start == 1
    assert intersection.rules[1].end == 1

    # test card
    assert mr1.get_card() == 11
    rules2 = [Range(1, 60), Range(None, None)]
    mr2 = MultiField(rules2)
    assert mr2.get_card() == 0
    rules4 = [WildcardExpr("01*1"), WildcardExpr("*11*")]
    mr4 = MultiField(rules4)
    assert mr4.get_card() == 8

    # test inclusion
    rules1 = [Range(10, 20), Range(10, 30)]
    rules2 = [Range(15, 20), Range(10, 10)]
    mr1 = MultiField(rules1)
    mr2 = MultiField(rules2)
    assert mr2 < mr1 is True
    assert mr1 < mr2 is False
    assert mr1 < mr1 is True

