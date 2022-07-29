This README is a summary of the information provided in the files of the project. <br />

**Data** folder: <br />
        - contains two subfolders, namely **Prices** and **Traits**, with CSV files for the NFT traits and price history <br />
        - the data in the CSV files is used in further computations <br />

**HGraphFiles** folder <br />
        - provides the data used in the PaToH partitioning <br />
        - contains two subfolders, namely **Input** and **Output**, with text files representing the input and output of the PaToH partitioner <br />
        - the files in the **Output** folder show the allocations of the vertices within the parts and are used in further computations <br />

**Tests** folder: <br />
        - Contains files with unit tests for the price partitioning algorithm developed and other utility functions <br />

**Main.py** file: <br />
        - the main methods are called here, on object instances of the *Hypergraph* and *Visualiser* classes <br />
        - in order to call the methods in Visualisation.py, one of *compute_partition_patoh()* and *compute_partition_by_price()* needs to be called before <br />
 
**Hypergraph.py** file: <br />
        - contains methods for processing the partitions resulted from partitioning the NFTs by PaToH and by price <br />
        - most methods are called on instances of the *Hypergraph* class, in *Main.py* <br />

**Visualisation.py** file: <br />
        - contains all the methods that can be used for the visualisation, including the draw_graph() which is the main method <br />
        - most methods are called on instances of the *Visualiser* class, in *Main.py* <br />

**Processing.py** file: <br />
        - contains the methods for the files and dictionaries processing <br />
        - includes methods which operate on the dictionaries of p-norms, NFT representations, traits information <br />

**PricePartitioning.py** file: <br />
        - contains the methods of the price partitioning algorithm implemented <br />
        - main method is partition_by_price(), called on a *Hypergraph* instance in *Main.py* <br />

**CONSTANTS.py** file: <br />
        - contains all the constants used in the project <br />
