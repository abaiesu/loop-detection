from loop_detection import WildcardExpr, Range, MultiField, loop_detection
from loop_detection.classes import Combination
from loop_detection.loop_detection_code import check_same_type, reformat_R
from loop_detection.generation.gen import generate_fw_tables, create_collection_rules


def get_cycles(result):

    cycles = set()
    for res in result:
        for edge in res[1]:
            intermediate = set()
            for e in edge:
                intermediate.add(e)
            cycles.add(frozenset(intermediate))
    return cycles


def test_correctness():

    fw_tables = {i : [] for i in range(4)}
    fw_tables[0] = [(Range(1,4, name = 'R1'), 1),
                    (Range(1,5, name = 'R2'), 1),
                    (Range(0,1, name = 'R3'), None),
                    (Range(0,5, name = 'H0'), None)]
    fw_tables[1] = [(Range(2,4, name = 'R4'), 3), (Range(0,5, name = 'H1'), None)]
    fw_tables[2] = [(Range(0, 4, name = 'R5'), 3), (Range(0,5, name = 'H2'), None)]
    fw_tables[3] = [(Range(2, 3, name = 'R6'), 1), (Range(4,5, name = 'R7'), None), (Range(0,5, name = 'H3'), None)]

    result_merged = loop_detection(fw_tables, merge= True)
    result_non_merged = loop_detection(fw_tables, merge= False)
    cycles_non_merged = get_cycles(result_merged)
    cycles_merged = get_cycles(result_non_merged)

    assert cycles_merged == cycles_non_merged

    for n in range(5, 20, 3):

        fw_tables = generate_fw_tables(n, max_range=20)

        result_merged = loop_detection(fw_tables, merge=True)
        result_non_merged = loop_detection(fw_tables, merge=False)

        cycles_merged = get_cycles(result_merged)
        cycles_non_merged = get_cycles(result_non_merged)

        assert len(cycles_merged) == len(cycles_non_merged)
        assert cycles_merged == cycles_non_merged


def test_check_type():

    R1 = create_collection_rules(20, num_fields_wc=1, num_fields_r=4)
    R2 = create_collection_rules(20, num_fields_wc=0, num_fields_r=5)
    R = R1 + R2
    assert not check_same_type(R)

    R1 = create_collection_rules(20, num_fields_wc=3, num_fields_r=4)
    R1 = reformat_R(R1)
    R2 = create_collection_rules(20, num_fields_wc=3, num_fields_r=4)
    R2 = reformat_R(R2)
    R = R1 + R2
    assert check_same_type(R)


