#!/usr/bin/env python
# coding: utf-8

from Bio import Phylo, AlignIO
from requests.exceptions import InvalidURL
from Bio.Align.Applications import MafftCommandline, ClustalwCommandline

import os
import sys
from sys import stderr
import fileinput
import requests


def get_sequences(accessions, output_file):
    print(accessions)
    open(output_file, 'w').close()

    # format of url to download sequence
    url_front = 'https://www.ncbi.nlm.nih.gov/search/api/sequence/'
    url_back = '/?report=fasta'

    # append each sequence to the combined fasta
    for a in accessions:
        try:
            u = url_front + str(a) + url_back
            r = requests.get(u)

            with open(output_file, 'ab') as f:
                f.write(r.content.rstrip())
                f.write("\n".encode("UTF-8"))

        except InvalidURL as err:
            print(err.message, file=stderr)
            print("Accession " + str(a) + " not fetched!!")

    # replace parentheses from organism names with * for tree formatting
    with fileinput.FileInput(output_file, inplace=True) as file:
        for line in file:
            print(line.replace('(', "*").replace(')', "*"), end='')


def mafft_align(in_file, options={'align_file_type': 'fa'}):
    mafft = "/home/mnygard/local/bin/mafft"

    # create mafft command line script object
    mafft_cline = MafftCommandline(mafft, input=in_file)
    if options['align_file_type'] == 'clustal':
        mafft_cline.clustalout = True
    out_file = "aligned." + options['align_file_type']

    # write stdout stream to alignment file
    stdout, stderr = mafft_cline()
    with open(out_file, "w") as f:
        f.write(stdout)

    return out_file


def clustalw_align(in_file, options={'align_file_type': 'clustal'}):
    cw2 = "/home/mnygard/local/bin/clustalw/clustalw2"

    clustalw_cline = ClustalwCommandline(cw2, infile=in_file)
    clustalw_cline.align = True
    clustalw_cline.output = options['align_file_type']
    clustalw_cline.outfile = 'clustal_aligned.aln'

    # execute the commandline object
    clustalw_cline()

    return 'clustal_aligned.aln'


def clustalw_tree(in_file, options={'outputtree': 'phylip'}):
    cw2 = "/home/mnygard/local/bin/clustalw/clustalw2"

    # create clustalw command line script object
    clustalw_cline = ClustalwCommandline(cw2, infile=in_file)
    clustalw_cline.tree = True
    clustalw_cline.outputtree = options['outputtree']
    clustalw_cline.quiet = True

    # execute the commandline object
    clustalw_cline()

    if options['outputtree'] == 'phylip':
        return in_file.split('.')[0] + '.ph'
    else:
        return in_file.split('.')[0] + '.tre'


def clustalw_bs(in_file, options={'bootstrap': 10, 'seed': 1000, 'outputtree': 'phylip'}):
    cw2 = "/home/mnygard/local/bin/clustalw/clustalw2"
    # create clustalw command line script object
    clustalw_cline = ClustalwCommandline(cw2, infile=in_file)
    clustalw_cline.bootstrap = options['bootstrap']
    clustalw_cline.seed = options['seed']
    clustalw_cline.bootlabels = 'node'
    clustalw_cline.outputtree = options['outputtree']

    # execute the commandline object
    clustalw_cline()

    if options['outputtree'] == 'phylip':
        return in_file.split('.')[0] + '.phb'
    else:
        return in_file.split('.')[0] + '.treb'


def add_names_to_tree(combined_file, tree_file):
    with open(combined_file) as f:
        raw = f.readlines()
    accToName = {}
    for raw_line in raw:
        if raw_line[0] == '>':
            r = raw_line.split()
            accession = r[0][1:-2]
            if '*' in r[2]:
                name = r[1]
            else:
                name = r[1] + ' ' + r[2]
            accToName[accession] = name
    for a, n in accToName.items():
        with fileinput.FileInput(tree_file, inplace=True) as file:
            for line in file:
                print(line.replace(a, a + ' ' + n), end='')


def test_clustalw_pipeline():
    print("fetching sequences...")
    get_sequences(accs, 'combined.fa')

    print("performing MSA...")
    clustalw_align('combined.fa', {'align_file_name': 'cw_aligned.aln', 'align_file_type': 'clustal'})

    print("generating ML tree...")
    clustalw_tree('cw_aligned.aln')

    print("boostrapping...")
    clustalw_bs('cw_aligned.aln')

    print("formatting tree...")
    add_names_to_tree('combined.fa', 'cw_aligned.phb')


def main():
    accession_string = input("Please enter a list of accession numbers separated by commas:")
    accs = accession_string.split(', ')
    msa_string = input("Please select a tool for performing MSA [mafft] or [clustal]:")
    if msa_string not in ['mafft', 'clustal']:
        print("Invalid tool choice! Exiting...")
        raise
    tree_string = input("Please select a tool for generating the tree [clustal] or [raxml]:")
    if tree_string not in ['clustal', 'raxml']:
        print("Invalid tool choice! Exiting...")
        raise

    prefix = input("Please enter a directory name to save files:")
    if not os.path.isdir(os.path.join(os.path.curdir, prefix)):
        os.mkdir(prefix)
    os.chdir(prefix)

    print("fetching sequences...")
    get_sequences(accs, "combined.fa")

    print("performing MSA...")
    if msa_string == 'mafft':
        aln = mafft_align("combined.fa")
    elif msa_string == 'clustal':
        aln = clustalw_align("combined.fa")

    # TODO: integrate RAxML application wrapper
    print("generating ML tree...")
    if tree_string == 'clustal':
        tree_file = clustalw_tree(aln)
    else:
        print("Cannot execute RAxML!!! Exiting...")
        raise

    print("boostrapping...")
    if tree_string == 'clustal':
        bootstrap = clustalw_bs(aln)
    else:
        print("Cannot execute RAxML!!! Exiting...")
        raise

    print("formatting tree...")
    if tree_string == 'clustal':
        add_names_to_tree('combined.fa', bootstrap)
        add_names_to_tree('combined.fa', tree_file)
    else:
        print("Cannot execute RAxML!!! Exiting...")
        raise

    visualize_string = input("Would you like to visualize the tree? [y/n]")
    if visualize_string in ['y', 'Y']:
        # tree_nexus = clustalw_tree(aln, {'outputtree': 'nexus'})
        bootstrap_nexus = clustalw_bs(aln, {'outputtree': 'nexus', 'bootstrap': 100, 'seed': 1000})
        tree = Phylo.read(bootstrap_nexus, 'nexus')
        Phylo.draw(tree)
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()


project_accs = ['EU346911', 'GQ504012', 'AM940158', 'AB514037', 'FN597581',
                'GQ352403', 'AJ781046', 'DQ845457', 'AM072819', 'GU390657',
                'AM072820', 'AM040493', 'GQ246672', 'AJ781047', 'D45063',
                'AB012594', 'X77447', 'X77439', 'EF373534', 'DQ256087', 'X77441',
                'X92492', 'AJ544063', 'DQ473536', 'AB282862', 'AM286414']
