# General information about the two collections
COLLECTION_SIZE = 10000

TRAIT_TYPES_BAYC = ['Background', 'Earring', 'Fur', 'Eyes', 'Mouth', 'Clothes', 'Hat']
TRAIT_TYPES_CRYPTOPUNKS = ['type', 'accessory']

BORED_APE_TTYPES_NO = 168
CRYPTOPUNKS_TTYPES_NO = 92

MIN_TRAITS_CRYPTOPUNKS = 1
MAX_TRAITS_CRYPTOPUNKS = 8

MIN_TRAITS_BAYC = 4
MAX_TRAITS_BAYC = 7

CRYPTOPUNKS = 'Cryptopunks'
BAYC = 'BoredApeYachtClub'

# Endpoints to access trait information
OPENSEA_API_URL = "https://api.opensea.io/api/v1/asset/"
ADDRESS_CRYPTOPUNKS_COLLECTION = "0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB/"  # idx 0 .. 9999
ADDRESS_BORED_APE_COLLECTION = "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/"  # idx 0 .. 9999

# Colours for the NFT nodes, from least to most expensive: Green, Yellow, Orange, Red
COLOR_DICT = {0: (0, 1, 0, 1), 1: (0.97, 0.988, 0.0585, 1), 2: (0.98, 0.636, 0.1, 1), 3: (1, 0, 0, 1)}

# Colours used in the visualisation
COLOR_INT_NET = (0.94, 0.56, 0.6, 0.3)
COLOR_EXT_NET = (0.99, 0.86, 0.33, 0.3)
COLOR_PATCH = (0.2, 0.4, 0.5, 0.1)
GRAY_COLOR = (0.5, 0.5, 0.5, 1)
GRAY_COLOR_SOFT = (0.5, 0.5, 0.5, 0.2)
WHITE_COLOR = (1, 1, 1, 1)

# Centers used in the visualisation
CANVAS_CENTER = (0, 0)
PART_RADIUS_INT = 0.5
PART_RADIUS_EXT = 0.5
PART_VERTICES = 0.3

# Payment tokens used in the sales
DAI = "DAI"
ETH = "ETH"
USDC = "USDC"
WETH = "WETH"

# Maximum imbalance allowed for the price partitioning algorithm
MAX_IMBALANCE_PART = 0.1

# Sales on or after this date are considered valid in the price analysis
VALID_DATE = "01/01/2020"

# Other information about the collections
MAX_TRADES_CRYPTOPUNKS = 15
NR_SALES_COLOR_VERTICES = [3, 7, 10, 15]
MAX_PRICE_BAYC = 2697000

# Used in the visualisation for colouring the nodes
NR_PRICE_RANGES = 4

# Subset of NFTs showing a complete net structure in the visualisation
NFTS_INTERNAL_NETS_CRYPTOPUNKS = [5822, 6965, 4850, 8024, 11, 4567, 344, 5684, 1860, 672, 1355, 706, 5670,
                                  1232, 4021, 851, 870, 834, 861, 1328, 1130, 832]
NFTS_INTERNAL_NETS_BAYC = [208, 481, 4882, 949, 3105, 950, 1115, 4130, 4179, 7581, 9909, 2133, 7534, 293, 1606]

# Subset of NFTs for the other parts, usedd in the visualisation
NFTS_EXTRA_CRYPTOPUNKS = [124, 138, 139, 8877, 3320, 3719, 4000, 5048, 5075, 7132, 8046, 8286, 8998, 9973, 9979, 9982, 9697, 9708, 9709]
NFTS_EXTRA_BAYC = [6, 16, 112, 3053, 3000, 3094, 3165, 5775, 6101, 7628, 7318, 9998, 8888]

# Types of node colouring in the visualisation
COLOR_NODES_LAST_SALE = 1
COLOR_NODES_NR_TRADES = 2
COLOR_NODES_PART_PRICE = 3

# Used in the price partitioning algorithm for checking the bounds
UNDEFINED_BOUND = -1

# Types of prices for NFTs
NFT_PRICE_LAST_SALE = 1
NFT_PRICE_AVG_SALES = 2

# Types of prices for traits with respect to NFTs
TRAIT_PRICE_AVG_NFTS = 1
TRAIT_PRICE_MEDIAN = 2
TRAIT_PRICE_AVG_AVG_NFTS = 3

# Used in the plots only
TRAIT_RARITY_PROB = 1
TRAIT_RARITY_CONN = 2
TRAIT_RARITY_PROB_VS_CONN = 3
PRICE_HISTOGRAM_LAST_SALE = 1
PRICE_HISTOGRAM_AVERAGE_SALES = 2
PRICE_HISTOGRAM_BOTH = 3

# Used for setting the parameters in the means computation
UNUSED = 0
PLUS_INFINITY = 1
MINUS_INFINITY = -1
NO_INFINITY = 0

# For the boxplots only
COLOR_PATCH_BOXPLOT = "#6da3d0"
COLOR_MEDIAN_BOXPLOT = "#255075"

# Used in computing the distances between vertices (similarity metrics)
N_METRIC = 1            # N_uv (number of common_nets)
M_METRIC = 2            # M_uv (Manhattan distance)
S_METRIC = 3            # S_uv (metric based on the size of common nets)
J_METRIC = 4            # J_uv (Jaccard coefficient)

# Used for rarity distributions visualisation for setting the ranges
ARITHMETIC_MEAN = 0
GEOMETRIC_MEAN = 1
OTHER_MEAN = -1