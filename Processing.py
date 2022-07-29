import csv
import math
import numpy as np
import pandas as pd
from math import log10

from CONSTANTS import *

collection_to_traits_file_dict = dict()
collection_to_last_sale_file_dict = dict()
collection_to_rep_file_dict = dict()
collection_to_all_sales_file_dict = dict()


# Used in the hypergraph construction
# Cryptopunks max imbalance = 0.09; BAYC max imbalance = 0.07
def get_output_file_path_PATOH(collection):
    perc = "009" if collection == CRYPTOPUNKS else "007"
    return "HGraphFiles/Output/hgraphfile_" + collection + "_10000_" + perc + ".part.3"


# Returns the traits file (ensures file is opened only once)
def get_traits_file(collection):
    if collection not in collection_to_traits_file_dict.keys():
        collection_to_traits_file_dict[collection] = pd.read_csv("Data/Traits/" + collection + "_Idx_Consecutive.csv")
    return collection_to_traits_file_dict[collection]


# Returns the last sales file (ensures file is opened only once)
def get_last_sales_file(collection):
    if collection not in collection_to_last_sale_file_dict.keys():
        collection_to_last_sale_file_dict[collection] = pd.read_csv("Data/Prices/Last_sales_" + collection + ".csv")
    return collection_to_last_sale_file_dict[collection]


# Returns the rep file (ensures file is opened only once)
def get_rep_file(collection):
    if collection not in collection_to_rep_file_dict.keys():
        collection_to_rep_file_dict[collection] = pd.read_csv("Data/Traits/" + collection + ".csv")
    return collection_to_rep_file_dict[collection]


# Returns the all-sales file (ensures file is opened only once)
def get_all_sales_file(collection):
    if collection not in collection_to_all_sales_file_dict.keys():
        collection_to_all_sales_file_dict[collection] = pd.read_csv("Data/Prices/All_sales_" + collection + ".csv")
    return collection_to_all_sales_file_dict[collection]


# Calculates the p_norms/gen mean of the trait probabilities
# General formula for gen mean: [1/n * (sum of xi^p)]^1/p with p -> +infinity for max, p -> -infinity for min
def get_p_norm_for_collection(collection, p, apply_log, divide_by_n, infinity):
    trait_prob = get_traits_probability(collection)
    rep_dict = get_rep_dict_consec(collection)
    p_norm_dict = dict()

    for i in range(COLLECTION_SIZE):
        probs = [trait_prob[t_idx] for t_idx in rep_dict[i]]
        p_norm_dict[i] = helper_calculate_p_norm(probs, p, apply_log, divide_by_n, infinity)

    return p_norm_dict


# Calculates the p-norm/mean for the probs
def helper_calculate_p_norm(probs, p, apply_log, divide_by_n, infinity):
    if infinity == NO_INFINITY:  # result depends on p
        if p == 0:  # geometric mean
            res = pow(np.product(probs), 1 / len(probs))
            if apply_log:  # (-1) * logarithm of base 10 for a positive result
                res = -log10(res)
            return res
        # Not geometric mean, compute result by the given formula
        res = sum([pow(prob, p) for prob in probs])
        if divide_by_n:
            res = res / len(probs)
        res = pow(res, 1 / p)
        if apply_log:
            res = -log10(res)
        return res
    # Else it's min or max
    res = probs
    if apply_log:
        res = [-math.log10(prob) for prob in probs]

    return min(res) if infinity == MINUS_INFINITY else max(res)


# Returns dict of (nft_id, list of (price, date)) for all sales of all NFTs
def get_all_sales_price(collection):
    file = "Data/Prices/All_sales_" + collection + ".csv"
    price_conversion_file = get_ETH_conversion_dict()
    all_trades_price = dict()

    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == 'id':
                continue
            token_id = int(row[0])
            last_sale = row[1]
            decimals = row[2]
            payment_token = row[3]
            date = row[4]

            if last_sale is not np.NAN:
                raw_price = int(last_sale)

                if int(float(decimals)) != 0:
                    raw_price = raw_price / math.pow(10, int(float(decimals)))
                price = get_price_in_USD(raw_price, payment_token, price_conversion_file, date)

                if token_id not in all_trades_price.keys():
                    all_trades_price[token_id] = []
                all_trades_price[token_id].append((price, date))

    return all_trades_price


# Returns the average sale price dict
def get_average_price_dict(collection):
    price_dict = dict()
    all_trades = get_all_sales_price(collection)
    valid_last_sales = get_last_sale_price_dict(collection)

    for n in valid_last_sales.keys():
        ts = [t[0] for t in all_trades[n]]  # Keep the price only
        if len(ts) == 0:
            raise Exception("Sale not present in the sales history for: " + str(n))
        price_dict[n] = np.mean(ts)

    return price_dict


# Returns the price value in USD given the payment token
# For ETH or WETH, convert to value of Ether from that day; for DAI or USDC price remains unchanged (value $1)
def get_price_in_USD(price, payment_token, price_conversion_file, date):
    if payment_token not in [ETH, WETH, DAI, USDC]:
        raise Exception("Payment token " + payment_token + " undefined.")

    if payment_token in [ETH, WETH]:
        price *= float(price_conversion_file[date])

    return price


# Returns dict of (date, ETH price); example: ('04/15/2022', ETH price)
def get_ETH_conversion_dict():
    conv_dict = dict()

    with open('Data/Prices/ETH_prices.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == 'date':
                continue
            conv_dict[row[0]] = row[1]

    return conv_dict


# Returns dict of (nft_id, last sale price) for valid dates and non-zero prices
def get_last_sale_price_dict(collection):
    csv_file = get_last_sales_file(collection)
    price_conv = get_ETH_conversion_dict()
    nodes_prices = dict()

    for i in range(COLLECTION_SIZE):
        token_id = int(csv_file.loc[i, 'id'])
        last_sale = csv_file.loc[i, 'last_sale']
        decimals = csv_file.loc[i, 'decimals']
        payment_token = csv_file.loc[i, 'payment_token']
        date = csv_file.loc[i, 'date']

        # Add sale only if valid
        if last_sale is not np.NAN and helper_is_valid_date(date):
            price = int(last_sale)
            if int(decimals) != 0:
                price = price / math.pow(10, int(decimals))
            nodes_prices[token_id] = get_price_in_USD(price, payment_token, price_conv, date)  # Convert to U.S. dollars

    return nodes_prices


# Returns dict of (trait index, probability) where probability = trait count / collection size
def get_traits_probability(collection):
    traits_number = get_traits_number(collection)
    traits_count = get_traits_count(collection)
    prob_dict = dict()

    for t_idx in range(traits_number):
        prob_dict[t_idx] = traits_count[t_idx] / COLLECTION_SIZE

    return prob_dict


# Returns the column net representation by treating each trait as a net
# column net rep: dict of (trait_idx, vertices) where the vertices are the pins of the net/trait
def get_col_net_rep(collection):
    rep_dict = get_rep_dict_consec(collection)
    column_net_rep = dict()

    for n in range(COLLECTION_SIZE):
        rep = rep_dict[n]
        for t_idx in rep:
            if t_idx not in column_net_rep.keys():
                column_net_rep[t_idx] = []
            column_net_rep[t_idx].append(n)

    return column_net_rep


# Returns dict of (trait type, dict of (trait value, index))
# index ranges from 0 to (traits_number - 1)
def get_traits_idx_consec(collection):
    csv_file = get_traits_file(collection)
    ttypes_dict = dict()

    for i in range(len(csv_file)):
        ttype = csv_file.loc[i, 'Type']
        value = csv_file.loc[i, 'Value']
        idx = csv_file.loc[i, 'Index']

        if ttype not in ttypes_dict.keys():
            ttypes_dict[ttype] = dict()
        ttypes_dict[ttype][value] = idx

    return ttypes_dict


# Returns the representation: dict of (nft_id, vector_rep) where vector_rep is a np array of the traits indexes
def get_rep_dict_consec(collection):
    csv_file = get_rep_file(collection)
    if len(csv_file) != COLLECTION_SIZE:
        raise Exception("NFTs represented in the CSV file is smaller than the size of the collection.")

    traits_idx = get_traits_idx_consec(collection)  # dict of (ttype, dict of (value, idx))
    types_arr = get_strings_types(collection)
    rep_dict = dict()

    for i in range(COLLECTION_SIZE):
        rep = []

        for t_type in types_arr:  # for each trait
            t_value = csv_file.loc[i, t_type]
            if t_value is not np.nan:

                # If Cryptopunks, merge 'accessory1',.. 'accessory7' into 'accessory'
                if collection == CRYPTOPUNKS and t_type in types_arr[1:]:
                    t_type = 'accessory'
                rep.append(traits_idx[t_type][t_value])

        rep_dict[i] = np.array(rep)

    return rep_dict


# Returns the total number of traits of the collection
def get_traits_number(collection):
    if collection == BAYC:
        return BORED_APE_TTYPES_NO

    if collection == CRYPTOPUNKS:
        return CRYPTOPUNKS_TTYPES_NO

    raise Exception("Collection " + collection + " undefined.")


# Returns a dict of (trait index, count) of the given collection
def get_traits_count(collection):
    if collection not in [BAYC, CRYPTOPUNKS]:
        raise Exception("Collection " + collection + " undefined.")

    csv_file = get_traits_file(collection)
    traits_nr = get_traits_number(collection)
    trait_count_dict = dict()

    for i in range(traits_nr):
        trait_count_dict[i] = csv_file.loc[i, 'Count']

    return trait_count_dict


# Returns the number of traits considered in the price analysis (after the VALID_DATE); (for BAYC = the traits count)
def get_trait_presence_in_price_analysis_dict(collection):
    if collection not in [BAYC, CRYPTOPUNKS]:
        raise Exception("Collection " + collection + " undefined.")

    if collection == BAYC:
        return get_traits_count(collection)

    presence = dict()
    rep_dict = get_rep_dict_consec(collection)
    last_sales_vs = get_last_sale_price_dict(collection).keys()

    # Count all the traits in the reps of the NFTs with valid last sales
    for n in last_sales_vs:
        rep = rep_dict[n]
        for idx in rep:
            if idx not in presence.keys():
                presence[idx] = 0
            presence[idx] += 1

    return presence


# Calculates the last sale price values for the ranges; the nr of price ranges is a predefined constant
# Helper for get_nodes_colour_by_last_sale_price
def helper_get_price_ranges_last_sale(collection):
    last_sales_dict = get_last_sale_price_dict(collection)
    vs_sorted = sorted(last_sales_dict.keys(), key=lambda n: last_sales_dict[n])
    vs_prices_sorted = [last_sales_dict[v] for v in vs_sorted]
    avg_elems = math.floor(len(last_sales_dict) / NR_PRICE_RANGES)

    # Calculate the range values
    ranges = [math.floor(vs_prices_sorted[avg_elems * (i + 1) - 1]) for i in range(NR_PRICE_RANGES - 1)]
    ranges.append(math.floor(vs_prices_sorted[len(last_sales_dict) - 1]))

    return ranges


# Returns the dict of colors for all vertices of the collection based on last sale price
def get_nodes_color_by_last_sale_price_dict(collection):
    last_sales_dict = get_last_sale_price_dict(collection)
    vs_prices = last_sales_dict.keys()
    price_ranges = helper_get_price_ranges_last_sale(collection)

    color_nodes_dict = dict()
    for nft_id in range(COLLECTION_SIZE):
        color = GRAY_COLOR  # Gray colour for a null price
        if nft_id in vs_prices:
            price = last_sales_dict[nft_id]

            # Calculate the index for the range of values
            idx = 0
            while idx < NR_PRICE_RANGES and price > price_ranges[idx]:
                idx += 1

            if idx == len(price_ranges):
                raise Exception("Current price is greater than max price defined in get_price_ranges().")

            color = COLOR_DICT[idx]
        color_nodes_dict[nft_id] = color

    # Compute the legend for the visualisation
    legend = dict()
    for i in range(len(price_ranges)):
        legend[i] = price_ranges[i]

    return color_nodes_dict, legend


# Returns the dict of colors for all vertices of the collection based on nr of sales
def get_nodes_color_by_nr_trades_dict(collection):
    nft_trades = get_all_sales_price(collection)
    color_nodes_dict = dict()

    for nft_id in range(COLLECTION_SIZE):
        color = GRAY_COLOR               # Gray colour for no sales

        if nft_id in nft_trades.keys():  # Sales exist for the current nft
            nft_trades_nr = len(nft_trades[nft_id])
            idx = 0

            # Compute the index for the colour
            while idx < len(NR_SALES_COLOR_VERTICES) and nft_trades_nr > NR_SALES_COLOR_VERTICES[idx]:
                idx += 1

            if idx == len(NR_SALES_COLOR_VERTICES):
                raise Exception("Current number of sales is greater than max price defined in get_price_ranges().")

            color = COLOR_DICT[idx]
        color_nodes_dict[nft_id] = color

    # Compute the legend for the visualisation
    legend = dict()
    for i in range(len(NR_SALES_COLOR_VERTICES)):
        legend[i] = NR_SALES_COLOR_VERTICES[i]

    return color_nodes_dict, legend


# Returns the trait for the given index
def get_trait_for_consec_idx(idx, collection):
    file = get_traits_file(collection)
    return file.loc[idx, 'Type'], file.loc[idx, 'Value']


# Returns the types of the CSV files
def get_strings_types(collection):
    if collection not in [BAYC, CRYPTOPUNKS]:
        raise Exception("Collection " + collection + " undefined.")

    if collection == BAYC:
        return TRAIT_TYPES_BAYC

    # For Cryptopunks the 'accessory' type is divided into 7 accessories
    return ['type', 'accessory1', 'accessory2', 'accessory3', 'accessory4', 'accessory5', 'accessory6',
            'accessory7']


# Given date format: MM/DD/YY
def get_day_month_year_from_date(date):
    month = int(date[:2])
    day = int(date[3:5])
    year = int(date[6:])

    return day, month, year


# To be a valid date, it must be at >= VALID_DATE
# Given date format: MM/DD/YY
def helper_is_valid_date(date):
    assert len(date) == len(VALID_DATE)

    curr_day, curr_month, curr_year = get_day_month_year_from_date(date)
    day, month, year = get_day_month_year_from_date(VALID_DATE)

    if curr_year != year:
        return curr_year > year

    if curr_month != month:
        return curr_month > month

    return curr_day >= day
