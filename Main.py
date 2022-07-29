from Hypergraph import *
from Visualisation import *

if __name__ == '__main__':
    collection = CRYPTOPUNKS
    vertices = list(range(10000))
    vertices_prices = list(get_last_sale_price_dict(collection).keys())
    parts = 3

    hypergraph = Hypergraph(collection, parts, is_price_filtered=False)

    hypergraph.compute_partition_patoh(NFTS_INTERNAL_NETS_CRYPTOPUNKS + NFTS_EXTRA_CRYPTOPUNKS)

    if not hypergraph.error_state:
        hypergraph.print_info_net_structure()
        visualiser = Visualiser(hypergraph)
        visualiser.draw_graph(node_color_type=NFT_PRICE_LAST_SALE)
    else:
        print("Visualisation can't proceed as no partition was produced.")
