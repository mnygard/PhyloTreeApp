# Phylogenetic Tree Generator (PTG) 
PTG is a prototype application that provides encapsulation of the workflow required to produce and visualize a
phylogenetic tree beginning with raw data in the form of NCBI accession numbers.

## Dependencies
* python 3.x
* mafft
* clustalw2
* RAxML (Currently not supported)
* BioPython (pip install biopython)

Please make sure mafft, clustal and RAxML binaries are included in your system PATH variable
 
## Usage
```shell script
$ python pipeline
```
Follow prompts. Note that RAxML functionality is currently not supported. Choosing RAxML for tree generation
will cause a crash. 

## Further Reading
The paper associated with this application is available [here](https://github.com/mnygard/PhyloTreeApp/blob/master/Nygard_Paper.pdf)




