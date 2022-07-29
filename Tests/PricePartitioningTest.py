from PricePartitioning import helper_next_indices, helper_calc_min_max_nr_elems, helper_get_internal_nets
from CONSTANTS import *


# Tests helper_get_internal_nets()
def test_helper_get_int_nets():
    vert_part_examples = [{1: 1, 10: 2, 3: 0, 19: 0, 55: 2, 48: 2},
                          {1: 1, 2: 2, 3: 0, 4: 0, 5: 2, 6: 2},
                          {1: 1, 10: 2, 3: 3, 19: 0, 55: 4, 48: 5},
                          {2: 0, 3: 0, 5: 0, 10: 0}]
    column_net_examples = [{10: [55], 14: [48, 1], 33: [10, 1, 3, 19, 55, 48], 100: [3, 19]},
                           {5: [3, 4], 9: [4, 5], 6: [1, 2]},
                           {10: [1, 3], 4: [55, 48, 2]},
                           {1: [2, 3, 10], 2: [5], 7: [2, 10]}]

    correct_results = [2, 1, 0, 3]
    for i in range(3):
        assert correct_results[i] == helper_get_internal_nets(vert_part_examples[i], column_net_examples[i])


# Tests helper_next_indices()
def test_next_indices():
    elems_nr_examples = [28, 20, 51, 23, 31, 10]
    indices_examples = [[7, 15, 27], [8, 19], [14, 29, 50], [3, 7, 22], [8, 17, 30], [3, 9]]
    parts_examples = [3, 2, 3, 3, 3, 2]
    correct_result_examples = [[[7, 17, 27], [8, 17, 27], [8, 18, 27], [9, 17, 27], [9, 18, 27], [9, 19, 27]],
                               [[9, 19], [10, 19]],
                               [[14, 31, 50], [14, 32, 50], [14, 33, 50], [15, 31, 50], [15, 32, 50], [15, 33, 50],
                                [15, 34, 50], [16, 31, 50],
                                [16, 32, 50], [16, 33, 50], [16, 34, 50], [16, 35, 50], [17, 32, 50], [17, 33, 50],
                                [17, 34, 50], [17, 35, 50],
                                [18, 33, 50], [18, 34, 50], [18, 35, 50]],
                               [[6, 14, 22], [7, 14, 22], [7, 15, 22]],
                               [[8, 19, 30], [9, 19, 30], [9, 20, 30], [10, 19, 30], [10, 20, 30], [10, 21, 30]],
                               [[4, 9], [5, 9]]]

    i = 0
    for indices in indices_examples:
        elems_nr = elems_nr_examples[i]
        parts = parts_examples[i]
        min_elems, max_elems = helper_calc_min_max_nr_elems(elems_nr, parts)
        r = indices.copy()
        result = []
        while len(r) != 0:
            r = helper_next_indices(r, min_elems, max_elems, parts, elems_nr)[0].copy()
            if len(r) != 0:
                result.append(r.copy())
        assert result == correct_result_examples[i]
        i += 1


# Tests helper_calc_min_max_nr_elems() with number of parts is between 2 and 4 inclusive
def test_min_max_nr_elems_result():
    assert MAX_IMBALANCE_PART == 0.1

    elems_nr = [3, 28, 28, 4, 10, 65, 65000]
    parts = [3, 3, 4, 2, 3, 3, 4]
    correct_results = [(0, 2), (8, 10), (6, 8), (1, 3), (2, 4), (18, 24), (14625, 17875)]

    for i in range(len(elems_nr)):
        min_elems, max_elems = helper_calc_min_max_nr_elems(elems_nr[i], parts[i])
        assert min_elems == correct_results[i][0]
        assert max_elems == correct_results[i][1]


if __name__ == '__main__':
    test_min_max_nr_elems_result()
    test_next_indices()
    test_helper_get_int_nets()
    print("----------All tests passed----------")
