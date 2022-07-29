from Processing import helper_calculate_p_norm, helper_is_valid_date, get_day_month_year_from_date
from CONSTANTS import *


# Tests helper_calculate_p_norm() (the computation of the p-norms/means)
def test_calculate_p_norm():
    tests = 7
    trait_probs = [[0.5, 0.17, 0.2], [0.8, 0.9], [0.45, 0.3, 0.4, 0.29], [0.19, 0.2, 0.7, 0.26], [0.8, 0.3], [0.9, 0.45],
                   [0.8, 0.5], [0.6, 0.2, 0.1, 0.15, 0.22]]
    p_arr = [1, 1, 0, 0, 4, 5, 5, 2]
    logs = [False, False, True, True, False, False, False, True]
    div_arr = [True, True, False, False, True, False, False, False]
    infs = [NO_INFINITY, NO_INFINITY, NO_INFINITY, NO_INFINITY, NO_INFINITY, PLUS_INFINITY, MINUS_INFINITY, NO_INFINITY]
    correct_results = [0.29, 0.85, 0.451, 0.54, 0.676, 0.9, 0.5, 0.039]

    for i in range(tests):
        result = helper_calculate_p_norm(probs=trait_probs[i], p=p_arr[i], apply_log=logs[i], divide_by_n=div_arr[i],
                                         infinity=infs[i])
        result = float("{:.3f}".format(result))
        assert result == correct_results[i]


# Tests helper_is_valid_date()
def test_valid_date():
    tests = 6
    dates = ["01/01/2020", "06/07/2020", "06/07/2022", "04/10/2019", "12/31/2019", "06/07/2017"]
    correct_results = [True, True, True, False, False, False]

    for i in range(tests):
        assert correct_results[i] == helper_is_valid_date(dates[i])


# Tests get_day_month_year_from_date() (format MM/DD/YY)
def test_get_day_month_year():
    tests = 3
    dates = ["09/14/2021", "06/07/2020", "04/10/2022"]
    correct_results = [(14, 9, 2021), (7, 6, 2020), (10, 4, 2022)]

    for i in range(tests):
        assert correct_results[i] == get_day_month_year_from_date(dates[i])


if __name__ == '__main__':
    test_calculate_p_norm()
    test_valid_date()
    test_get_day_month_year()
    print("----------All tests passed----------")
