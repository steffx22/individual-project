from PricePartitioning import *
from Processing import *
from collections import Counter


class Hypergraph:

    def __init__(self, collection, nr_parts, is_price_filtered):
        print("----------Initialising the hypergraph----------")

        self.collection = collection  # collection name
        if collection not in [CRYPTOPUNKS, BAYC]:
            raise Exception("Methods for collection " + collection + " have not been implemented yet.")

        self.nr_parts = nr_parts  # number of parts
        self.is_price_filtered = is_price_filtered  # all NFTs or price is filtered
        self.file_parts = get_output_file_path_PATOH(collection)  # file for reading PaToH partitioning
        self.col_net_rep = get_col_net_rep(collection)  # construct column net represenation
        self.vert_part = dict()  # dict (vertex, part)
        self.part_vert = dict()  # dict (part, vertices)
        self.vs_subset = []  # subset used for visualisation

        # The following are computed in process_hypergraph()
        self.int_nets = dict()  # dict (net_id, nets); net_id is a visualisation label
        self.ext_nets = dict()  # dict (net_id, nets); net_id is a visualisation label
        self.net_conn = dict()  # dict of (net_idx, connectivity)
        self.int_nets_idx = []  # indexes of the internal nets
        self.ext_nets_idx = []  # indexes of the external nets

        # The following have been filtered for visualisation wrt vs_subset
        self.col_net_rep_filtered = dict()
        self.vert_part_filtered = dict()
        self.part_vert_filtered = dict()

        # Used in computing the connectivities and in the visualisation
        self.by_price = False
        self.price_type = UNUSED

        # If error_state, visualisation can't proceed
        self.error_state = False

    def process_hypergraph(self, vs_subset):
        print("----------Processing the hypergraph----------")
        if not 2 <= self.nr_parts <= 4:
            raise Exception("The price and PaToH partitioning is defined only for 2, 3 or 4 parts.")

        self.vs_subset = vs_subset
        size = 0
        # Split nets into external and internal
        for net_idx in self.col_net_rep.keys():
            vs = self.col_net_rep[net_idx]
            vs_curr = list(set(vs).intersection(set(self.vs_subset)))

            if len(vs_curr) >= 1:  # At least one vertex
                t_type, t_value = get_trait_for_consec_idx(net_idx, self.collection)
                net_ident = helper_get_trait_ident(t_type, t_value)

                if self.by_price:   # consider only NFTs with last sale price
                    connectivity = len(set([self.vert_part[v] for v in vs if v in self.vert_part.keys()]))
                else:
                    connectivity = len(set([self.vert_part[v] for v in vs]))

                # Update dicts for visualisation
                if connectivity == 1:  # internal net
                    self.int_nets[net_ident] = vs_curr
                    self.int_nets_idx.append(net_idx)
                else:                  # external net
                    #if size < 6:
                    #size += 1
                    self.ext_nets[net_ident] = vs_curr
                    self.ext_nets_idx.append(net_idx)

                # Update other fields
                self.net_conn[net_idx] = connectivity
                self.col_net_rep_filtered[net_idx] = vs_curr
            else:
                print("Net " + str(net_idx) + " doesn't have any vertices and won't be considered.")

        # Filter the partitions dicts to correspond to the subset
        self.vert_part_filtered = {v: p for v, p in self.vert_part.items() if v in self.vs_subset}
        self.part_vert_filtered = helper_get_part_vert(self.vert_part_filtered)

        if [] in self.part_vert_filtered.values():
            raise Exception("Part without vertices found.")

    def compute_partition_patoh(self, vs_subset):
        print("----------Reading the partition----------")
        self.read_partitions_from_file(self.file_parts)
        self.by_price = False
        self.process_hypergraph(vs_subset)

    def compute_partition_by_price(self, vs_subset, price_type, price_bound_l, price_bound_r):
        print("----------Computing the partition----------")
        assert self.is_price_filtered
        if price_type not in [NFT_PRICE_AVG_SALES, NFT_PRICE_LAST_SALE]:
            raise Exception("Price type " + str(price_type) + " not defined.")

        self.by_price = True
        self.price_type = price_type
        self.vert_part = partition_by_price(self.collection, self.nr_parts, self.col_net_rep, vs_subset, price_type,
                                            price_bound_l, price_bound_r)

        if self.vert_part is None:
            self.error_state = True
        else:
            self.process_hypergraph(self.vert_part.keys())
            self.part_vert = helper_get_part_vert(self.vert_part)

    def compute_similarity_partitioning(self, metric):
        if self.by_price:
            raise Exception("Similarity is computed for all vertices for the partition produced by PaToH.")

        reps = get_rep_dict_consec(self.collection)
        trait_counts = get_traits_count(self.collection)

        print("\n----------Vertices in each part----------\n")
        for p in range(self.nr_parts):
            vs = self.part_vert[p]
            internal_sim_results = []

            for i in range(len(vs) - 1):
                rep1 = reps[vs[i]]
                for j in range(i + 1, len(vs)):
                    rep2 = reps[vs[j]]
                    internal_sim_results.append(helper_calc_similarity(metric, rep1, rep2, trait_counts))

            print("Part " + str(p + 1), "(internal) --- Average, median of the similarity metric results: ",
                  np.mean(internal_sim_results), np.median(internal_sim_results))

        print("\n----------Vertices in different parts----------\n")
        for p1 in range(self.nr_parts):
            vs1 = self.part_vert[p1]
            other_vs = []
            for p2 in range(self.nr_parts):
                if p2 != p1:
                    vs2 = self.part_vert[p2]
                    for v in vs2:
                        other_vs.append(v)

            external_sim_results = []
            for v1 in vs1:
                rep1 = reps[v1]
                for v2 in other_vs:
                    rep2 = reps[v2]
                    external_sim_results.append(helper_calc_similarity(metric, rep1, rep2, trait_counts))

            print("Part " + str(p1 + 1), "(external) --- Average, median of the similarity metric results: ",
                  np.mean(external_sim_results), np.median(external_sim_results))

    # Prints details about the trait probabilities related to net connectivities
    def print_connectivity_prob_info(self):
        assert not self.by_price
        rep_dict = get_rep_dict_consec(self.collection)
        trait_probs = get_traits_probability(self.collection)

        print("\nNumber of elements in each part: " + str([len(self.part_vert[p]) for p in range(self.nr_parts)]) + "\n")

        print("\n----------Connectivity distributions----------")
        for p in range(self.nr_parts):
            # Print connectivity distribution
            conns = Counter([self.net_conn[t_idx] for v in self.part_vert_filtered[p] for t_idx in rep_dict[v]])
            print("Part " + str(p + 1) + ": " + str(conns), "--- Average connectivities: " + str(
                {c: (sum([conns[c]]) / len(self.part_vert[p])) for c in conns.keys()}))

        print("\n----------Trait probabilities----------")
        for p in range(self.nr_parts):
            # Print trait probabilities for each net connectivity
            prob = [trait_probs[t] for t in self.net_conn.keys() if self.net_conn[t] == (p + 1)]
            if len(prob) != 0:
                print("Net connectivity " + str(p + 1) + " (min, max, avg, median): ", min(prob),
                      max(prob), np.mean(prob), np.median(prob))

    # Prints internal and external nets with number of links, ranking and average price
    def print_info_net_structure(self):
        trait_count = get_traits_count(self.collection)

        print("\n----------Internal Nets----------")
        sorted_int_nets_idx = sorted(self.int_nets_idx, key=lambda n: trait_count[n])

        for int_net in sorted_int_nets_idx:
            # Get trait type and value to print
            trait_type, trait_value = get_trait_for_consec_idx(int_net, self.collection)
            int_net_ident = helper_get_trait_ident(trait_type, trait_value)     # label for the net

            vs = self.col_net_rep_filtered[int_net]
            print(int_net_ident + " --- net size: " + str(trait_count[int_net]) + " --- part: "
                  + str(self.vert_part_filtered[vs[0]] + 1))
            if self.by_price:
                print("--->", str(len(vs)), "NFTs with it:", str(vs))

        print("\n----------External Nets----------")
        sorted_ext_nets_idx = sorted(self.ext_nets_idx, key=lambda n: trait_count[n])
        for ext_net in sorted_ext_nets_idx:
            # Get trait type and value to print
            t_type, t_value = get_trait_for_consec_idx(ext_net, self.collection)
            ext_net_ident = helper_get_trait_ident(t_type, t_value)     # label for the net

            vs = self.col_net_rep_filtered[ext_net]
            print(ext_net_ident + " --- net size: " + str(trait_count[ext_net]) + " --- connectivity: "
                  + str(self.net_conn[ext_net]) + (
                      (" --- NFTs with it in the part: " + str(len(vs))) if self.by_price else ''))

    # Returns the actual name of the collection
    def get_name_str(self):
        if self.collection == CRYPTOPUNKS:
            return self.collection

        return 'Bored Ape Yacht Club'

    # Reads and assigns to the fields the dicts of (part, vertices) and (vertex, part)
    def read_partitions_from_file(self, file_path):
        f = open(file_path, "r")
        line = f.readline()
        v_idx = 0

        while line:
            self.vert_part[v_idx] = int(line)
            v_idx = v_idx + 1
            line = f.readline()

        f.close()
        self.part_vert = helper_get_part_vert(self.vert_part)

    # Constructs the hypergraph file used in the PaToH partitioning
    def construct_hgraph_file(self, file_path):
        f = open(file_path, "w")

        # Calculate the total number of pins (links between nets and vertices i.e. size of the nets)
        pins = 0
        for n in self.col_net_rep.keys():
            pins += len(self.col_net_rep[n])

        nets = get_traits_number(self.collection)

        # Write the sizes
        f.write(str(0) + " " + str(COLLECTION_SIZE) + " " + str(nets) + " " + str(pins) + "\n")

        # Write the vertices of each net (indexed from 0 to (nets - 1))
        for n in range(nets):
            vs = self.col_net_rep[n]
            for v in vs:
                f.write(str(v) + " ")
            f.write("\n")

        f.close()


# Constructs the labels of the visualisation vertices given the type and value of the trait
def helper_get_trait_ident(ttype, value):
    return ttype[0] + " - " + value


# Helper method for calculating internal and external similarity based on specific formula
def helper_calc_similarity(metric, rep1, rep2, trait_counts):
    if metric == N_METRIC:
        return len([n for n in rep1 if n in rep2])

    if metric == M_METRIC:
        nr_common_nets = len([n for n in rep1 if n in rep2])
        return len(rep1) + len(rep2) - 2 * nr_common_nets

    if metric == J_METRIC:
        nr_common_nets = len([n for n in rep1 if n in rep2])
        return nr_common_nets / (len(rep1) + len(rep2) - nr_common_nets)

    if metric == S_METRIC:
        common_nets = [n for n in rep1 if n in rep2]
        return sum([1 / (trait_counts[n] - 1) for n in common_nets])

    raise Exception("Metric " + str(metric) + " not implemented yet.")


# Computes the dict of (part, vertices) given the dict of (vertex, part)
def helper_get_part_vert(vert_part):
    part_vert = dict()

    for v in vert_part.keys():
        p = vert_part[v]
        if p not in part_vert.keys():
            part_vert[p] = []

        part_vert[p].append(v)

    return part_vert


# Returns top n NFTs with the highest price
def helper_vis_get_vertices_highest_price(collection, n):
    last_sale_prices = get_last_sale_price_dict(collection)
    sorted_vs_by_prices = {net_id: v for net_id, v in
                             sorted(last_sale_prices.items(), key=lambda item: item[1], reverse=True)}
    return list(sorted_vs_by_prices.keys())[:n]


# Returns top n NFTs with the greatest number of sales
def helper_vis_get_max_nr_sales_vertices(collection, n):
    all_sales_prices = get_all_sales_price(collection)
    sorted_vs_by_sales_nr = sorted(all_sales_prices.keys(), key=lambda v: len(all_sales_prices[v]), reverse=True)

    return sorted_vs_by_sales_nr[:n]


# Filters the given subset to keep only vertices with last sale price
def helper_vis_filter_vs_without_price(collection, vs_subset):
    v_prices = get_last_sale_price_dict(collection).keys()
    return [v for v in vs_subset if v in v_prices]


def helper_vis_get_vertices_with_nr_traits(collection, traits_number):
    if collection == CRYPTOPUNKS and not MIN_TRAITS_CRYPTOPUNKS <= traits_number <= MAX_TRAITS_CRYPTOPUNKS:
        raise Exception("Number of traits is doesn't exist for the collection. Min and max allowed: "
                        + str(MIN_TRAITS_CRYPTOPUNKS) + " " + str(MAX_TRAITS_CRYPTOPUNKS))
    elif collection == BAYC and not MIN_TRAITS_BAYC <= traits_number <= MAX_TRAITS_BAYC:
        raise Exception("Number of traits is doesn't exist for the collection. Min and max allowed: "
                        + str(MIN_TRAITS_BAYC) + " " + str(MAX_TRAITS_BAYC))

    vs = []
    reps = get_rep_dict_consec(collection)

    for v in reps.keys():
        rep = reps[v]
        if len(rep) == traits_number:
            vs.append(v)

    print("Number of NFTs with " + str(traits_number) + " traits:", len(vs))
    return vs


# Returns NFTs with digit 8 in their number
def helper_vis_get_NFTs_with_digit_8(collection):
    vs = []
    reps = get_rep_dict_consec(collection)

    for v in reps.keys():
        if '8' in str(v):
            vs.append(v)

    return vs


# Returns the NFTs which have the trait t_idx
def helper_vis_get_NFTs_with_trait(collection, t_idx):
    reps = get_rep_dict_consec(collection)
    vs = []

    for n in reps.keys():
        if t_idx in reps[n]:
            vs.append(n)

    return vs


# Prints average Ether values starting with 2020
def helper_print_avg_ETH_values():
    ETH_values = get_ETH_conversion_dict()
    for year in ["2020", "2021", "2022"]:
        vs = []
        for date in ETH_values.keys():
            curr_year = date[6:10]
            value = float(ETH_values[date])
            if curr_year == year:
                vs.append(value)
        print("Average in " + year, np.average(vs))


# Prints how many traits are considered in the price analysis for Cryptopunks
def helper_print_traits_presence_Cryptopunks():
    top_10_rarest_traits = [4, 3, 81, 71, 34, 76, 87, 89, 73, 2]
    traits_count = get_traits_count(CRYPTOPUNKS)
    traits_presence = get_trait_presence_in_price_analysis_dict(CRYPTOPUNKS)
    sorted_traits_by_count = sorted(traits_count.keys(), key=lambda t: traits_count[t])

    for t_idx in sorted_traits_by_count:
        t_type, t_value = get_trait_for_consec_idx(t_idx, CRYPTOPUNKS)
        print(t_value, ("(top 10 rarest trait) " if t_idx in top_10_rarest_traits else "") + "--- present for",
              traits_presence[t_idx], "NFTs out of", traits_count[t_idx])