import time

from Processing import *
from CONSTANTS import *


# Partitions the NFTs in vs_subset; considers only NFTs with price within the given price bounds
def partition_by_price(collection, nr_parts, col_net_rep, vs_subset, price_type, price_bound_l, price_bound_r):
    start_time = time.time()

    # Get the appropriate price dictionaries
    if price_type == NFT_PRICE_LAST_SALE:
        prices = get_last_sale_price_dict(collection)
    else:
        if price_type != NFT_PRICE_AVG_SALES:
            raise Exception("Price type " + str(price_type) + " not defined.")

        prices = get_average_price_dict(collection)

    # Keep for partitioning only vertices within the bounds given
    vs_subset_filtered = {k: v for k, v in prices.items() if k in vs_subset}
    if price_bound_l == UNDEFINED_BOUND and price_bound_r == UNDEFINED_BOUND:   # all prices
        vs_dict_filtered = {nft_id: p for nft_id, p in sorted(vs_subset_filtered.items(), key=lambda item: item[1])}
    elif price_bound_l == UNDEFINED_BOUND:                                      # price <= price_bound_r
        vs_dict_filtered = {nft_id: p for nft_id, p in sorted(vs_subset_filtered.items(), key=lambda item: item[1]) if
                            p <= price_bound_r}
    elif price_bound_r == UNDEFINED_BOUND:                                      # price >= price_bound_l
        vs_dict_filtered = {nft_id: p for nft_id, p in sorted(vs_subset_filtered.items(), key=lambda item: item[1]) if
                            p >= price_bound_l}
    else:
        vs_dict_filtered = {nft_id: p for nft_id, p in sorted(vs_subset_filtered.items(), key=lambda item: item[1]) if
                            price_bound_l <= p <= price_bound_r}

    # Keep the order of the sorted vertices
    sorted_vs = list(vs_dict_filtered.keys())
    total_elems = len(sorted_vs)
    print("Total number of elements to partition: " + str(total_elems))

    # Calculate minimum and maximum imbalance allowed
    min_elems, max_elems = helper_calc_min_max_nr_elems(total_elems, nr_parts)
    indices = [min_elems * k - 1 for k in range(1, nr_parts)] + [total_elems - 1]
    best_nr_nets = 0
    best_imbalance = 1.0        # Updated if lower imbalance found
    best_indices = []
    avg_imbalance = 1.0

    # Check if current indices are already balanced
    do_next = False
    for p in range(len(indices)):
        curr_elems = indices[p] + 1 if p == 0 else indices[p] - indices[p - 1]
        if not min_elems <= curr_elems <= max_elems:    # Imbalanced
            do_next = True
            break

    # If not already balanced, calculate next indices
    if do_next:
        indices, avg_imbalance = helper_next_indices(indices, min_elems, max_elems, nr_parts, total_elems)

    # While we have next indices
    while len(indices) != 0:
        print(indices, avg_imbalance)

        # Calculate number of internal nets
        curr_vert_part = helper_get_vert_part_from_indices(indices, sorted_vs)
        result = helper_get_internal_nets(curr_vert_part, col_net_rep)

        # Update best results
        if result > best_nr_nets or (result == best_nr_nets and avg_imbalance < best_imbalance):
            best_indices = list.copy(indices)
            best_nr_nets = result
            best_imbalance = avg_imbalance

        # Get the next indices
        indices, avg_imbalance = helper_next_indices(indices, min_elems, max_elems, nr_parts, total_elems)

    if best_nr_nets > 0:
        best_vert_part = helper_get_vert_part_from_indices(best_indices, sorted_vs)
        print("Price partitioning running time: " + str(time.time() - start_time))
        return best_vert_part

    print("No internal nets found.")
    print("Price partitioning running time: " + str(time.time() - start_time))
    return None


# Calculates the next delimiters of the indices for the parts
def helper_next_indices(indices, min_elems, max_elems, parts, total_elems):
    if not 2 <= parts <= 4:     # cCurrent efficiency of the algorithm allows partitioning for 2, 3 or 4 parts
        raise Exception("Number of parts " + str(parts) + " not within [2, 4].")

    if len(indices) == 0:
        return [], 1

    curr_part = parts - 2

    # Try to increase the current elements
    increased_curr_val = -1
    while curr_part >= 0:
        prev = 0 if curr_part == 0 else indices[curr_part - 1]
        increased_curr_val = -1
        max_range = prev + max_elems + 1 if curr_part > 0 else max_elems

        # Check if any delimiter can be increased
        for i in range(indices[curr_part] + 1, max_range):
            rem_elems = total_elems - i - 1
            rem_parts = parts - curr_part - 1
            if rem_parts * min_elems <= rem_elems <= rem_parts * max_elems:     # Can be increased
                increased_curr_val = i
                break

        if increased_curr_val != -1:    # Break from while loop
            break

        curr_part -= 1

    # No element can be further increased, no next indices exist
    if curr_part < 0:
        return [], 1

    # Increase current elem to increased_curr_val (ensured by previous check)
    indices[curr_part] = increased_curr_val
    curr_part += 1

    # Recalculate the indices on the following positions
    while curr_part < parts - 1:
        # Try with every value, starting with minimum
        for i in range(indices[curr_part - 1] + min_elems, indices[curr_part - 1] + max_elems + 1):
            rem_elems = total_elems - i - 1
            rem_parts = parts - curr_part - 1

            # Break from for when smallest value found
            if rem_parts * min_elems <= rem_elems <= rem_parts * max_elems:
                indices[curr_part] = i
                break

        curr_part += 1

    return indices.copy(), helper_calculate_avg_imbalance(indices)


# Returns number of internal nets (of the vertices partitioned only)
def helper_get_internal_nets(vert_part, column_net_rep):
    int_nets = 0
    vs_partitioned = vert_part.keys()

    for net_idx in column_net_rep.keys():
        vs = column_net_rep[net_idx]
        parts = set([vert_part[v] for v in vs if v in vs_partitioned])

        # Internal net when vertex belongs to one part only
        if len(parts) == 1:
            int_nets += 1

    return int_nets


# Computes the dict of (vertex, part) from the list of delimiters, i.e. indices
# sorted_vs preserves the order of the vertices
def helper_get_vert_part_from_indices(indices, sorted_vs):
    k_part = len(indices)
    vert_part = dict()

    # Vertices in the first sector belong to part 1
    for v in sorted_vs[:(indices[0] + 1)]:
        vert_part[v] = 0

    # Vertices in the next sectors belong to next parts
    for p in range(1, k_part):
        curr_vs = sorted_vs[(indices[p - 1] + 1):(indices[p] + 1)]
        for v in curr_vs:
            vert_part[v] = p

    return vert_part


# Calculate min and max nr of elements allowed in each part under predefined max imbalance
def helper_calc_min_max_nr_elems(elems_nr, k_part):
    avg_elems_per_part = int(elems_nr / k_part)
    min_elems = math.floor(avg_elems_per_part - avg_elems_per_part * MAX_IMBALANCE_PART)
    max_elems = math.ceil(avg_elems_per_part + avg_elems_per_part * MAX_IMBALANCE_PART)

    print("Total number of elements: " + str(elems_nr) + ". Average elements per part: " + str(avg_elems_per_part) +
          ". Min and max number of elements per part: " + str(min_elems) + ", " + str(max_elems) + ".")

    return min_elems, max_elems


# Calculates average imbalance of the parts (used in price partitioning)
def helper_calculate_avg_imbalance(indices):
    parts = len(indices)
    total_elems = indices[parts - 1] + 1
    avg = total_elems / parts

    curr_avg_imbalance = abs(1 - ((indices[0] + 1) / avg))      # Imbalance of the first part

    for i in range(1, len(indices)):                            # Imbalance of the rest of the parts
        elems = indices[i] - indices[i - 1]
        curr_avg_imbalance += abs(1 - (elems / avg))

    # Divide total imbalance by the nr of parts
    curr_avg_imbalance /= parts

    return curr_avg_imbalance

