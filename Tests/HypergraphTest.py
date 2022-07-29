from Hypergraph import helper_calc_similarity, helper_get_part_vert
from CONSTANTS import *


# Tests helper_calc_similarity() with all four metrics
def test_helper_calc_similarity():
    tests = 12
    rep1 = [[0, 1, 10], [9, 10, 2, 3], [4, 5, 9, 3], [2, 1], [9, 8, 7], [10, 7, 2], [4, 5], [8, 9, 2], [7, 3, 4, 1, 0],
            [9, 3, 7], [8, 4, 5, 6], [8, 2, 4, 5]]
    rep2 = [[10, 2, 3], [9, 8, 2, 3], [4, 2, 9, 0], [3, 1], [3, 0, 7], [8, 10, 2], [0, 5, 1, 6], [8, 9, 10],
            [7, 0, 2, 10, 4], [1, 5, 7, 2], [4, 7, 5, 9], [7, 2, 8, 5]]
    trait_counts = {0: 12, 1: 8, 2: 55, 3: 46, 4: 2, 5: 6, 6: 10, 7: 5, 8: 11, 9: 100, 10: 22}
    metrics = [M_METRIC, M_METRIC, M_METRIC, N_METRIC, N_METRIC, N_METRIC, S_METRIC, S_METRIC, S_METRIC, J_METRIC,
               J_METRIC, J_METRIC]
    correct_results = [4, 2, 4, 1, 1, 2, 0.2, 0.11, 1.341, 0.167, 0.333, 0.6]
    for i in range(tests):
        result = helper_calc_similarity(metrics[i], rep1[i], rep2[i], trait_counts=trait_counts)
        result = float("{:.3f}".format(result))
        assert correct_results[i] == result


# Tests helper_get_part_vert()
def test_helper_get_part_vert():
    tests = 3
    vert_parts = [{3: 1, 5: 2, 7: 2, 1: 10, 9: 10}, {6: 4, 10: 5, 1: 5, 0: 0, 2: 0, 7: 7}, {8: 8}]
    correct_results = [{1: [3], 2: [5, 7], 10: [1, 9]}, {4: [6], 5: [10, 1], 0: [0, 2], 7: [7]}, {8: [8]}]

    for i in range(tests):
        assert correct_results[i] == helper_get_part_vert(vert_parts[i])


if __name__ == '__main__':
    test_helper_calc_similarity()
    test_helper_get_part_vert()
    print("----------All tests passed----------")
