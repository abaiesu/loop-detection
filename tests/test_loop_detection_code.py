from loop_detection import WildcardExpr, Range, MultiField, loop_detection
from loop_detection.algo.combination import Combination
from loop_detection.loop_detection_code import check_same_type
import pytest


def test_check_same_type():
    R1 = [Range(0, 1), Range(4, 8), WildcardExpr("*")]
    assert check_same_type(R1) is False

    R2 = [Range(5, 9), Range(9, 10)]
    assert check_same_type(R2) is True

    R3 = [MultiField([Range(9, 10)]), MultiField([Range(9, 10), Range(0, 8)])]
    assert check_same_type(R3) is False

    R4 = [MultiField([Range(9, 10), Range(0, 8)]), MultiField([Range(9, 10), Range(0, 8)])]
    assert check_same_type(R4) is True

    R5 = [MultiField([Range(9, 10), WildcardExpr("*")]), MultiField([Range(9, 10), Range(0, 8)])]
    assert check_same_type(R5) is False

    R6 = [MultiField([Range(9, 10), WildcardExpr("*")]), MultiField([Range(9, 10), WildcardExpr("*0")])]
    assert check_same_type(R6) is True


def test_loop_detection():
    fw_tables = {i: [] for i in range(4)}

    fw_tables[0] = [('R1', Range(1, 5), 1),
                    ('R2', Range(1, 4), 1),
                    ('R3', Range(0, 1), None),
                    ('H0', Range(0, 5), None)]

    fw_tables[1] = [('R4', Range(2, 4), 3),
                    ('H1', Range(0, 5), None)]

    fw_tables[2] = [('R5', Range(0, 4), 3),
                    ('H2', Range(0, 5), None)]

    fw_tables[3] = [('R7', Range(2, 3), 1),
                    ('R6', Range(4, 5), None),
                    ('H3', Range(0, 5), None)]

    result = loop_detection(fw_tables)

    assert result == [(Combination(Range(2, 3)), [[1, 3]])]
