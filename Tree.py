from Bio import Phylo
from requests.exceptions import InvalidURL
from Bio.Align.Applications import MafftCommandline  # ClustalwCommandline
from Bio.Phylo.Applications import RaxmlCommandline
from Bio.Application import ApplicationError
import pylab
import os
import shutil
from sys import stderr
import fileinput
import requests
from settings import BASEDIR
from messages import error
from testData import project_accs
from importlib import import_module


class Tree:
    def __init__(self, name, seqs=None, msaTool=None, treeTool=None):
        if None in [seqs, msaTool, treeTool]:
            self.name = name
            self.dir = os.path.join(BASEDIR, 'media', name)
            if not os.path.isdir(self.dir):
                self.fatal_error(error.UNABLE_TO_LOAD_TREE)
            else:
                s = import_module('.settings', 'media.' + name)
                self.seqs = s.SEQS.split(', ')
                self.msaTool = s.MSA_TOOL
                self.treeTool = s.TREE_TOOL
        else:
            self.name = name
            self.seqs = seqs
            self.msaTool = msaTool
            self.treeTool = treeTool
            self.dir = os.path.join(BASEDIR, 'media', name)
            if os.path.isdir(self.dir):
                print("Overwriting previous tree: " + self.name)
                shutil.rmtree(self.dir)
            os.mkdir(self.dir)
            with open(os.path.join(self.dir, 'settings.py'), 'w') as f:
                f.write("SEQS = " + "'" + ', '.join(self.seqs) + "'" + '\n')
                f.write("MSA_TOOL = " + "'" + self.msaTool + "'" + '\n')
                f.write("TREE_TOOL = " + "'" + self.treeTool + "'" + '\n')

    def fatal_error(self, message):
        print(message, file=stderr)
        self.__init__(self.name, None, None, None)

    def get_sequences(self):
        print("fetching sequences...")
        combined_file = os.path.join(self.dir, 'combined.fa')

        # format of url to download sequence
        url_front = 'https://www.ncbi.nlm.nih.gov/search/api/sequence/'
        url_back = '/?report=fasta'

        # append each sequence to the combined fasta
        for a in self.seqs:
            try:
                u = url_front + str(a) + url_back
                r = requests.get(u)
                with open(combined_file, 'ab') as f:
                    f.write(r.content.rstrip())
                    f.write("\n".encode("UTF-8"))
            except InvalidURL as err:
                print(err.strerror, file=stderr)
                print("Accession " + str(a) + " not fetched!!")

        # replace parentheses from organism names with * for tree formatting
        with fileinput.FileInput(combined_file, inplace=True) as file:
            for line in file:
                print(line.replace('(', "*").replace(')', "*"), end='')

    def align(self):
        print("performing multiple sequence alignment...")
        if self.msaTool == 'mafft':
            self._mafft_align()
        elif self.msaTool == 'clustal':
            # self._clustal_align()
            self.fatal_error(error.INVALID_ALIGNER)
            return
        else:
            self.fatal_error(error.INVALID_ALIGNER)
            return

    def _mafft_align(self):
        try:
            mafft_cline = MafftCommandline(input=os.path.join(self.dir, 'combined.fa'))
        except ApplicationError:
            mafft_cline = None
            self.fatal_error(error.MafftErrorMessage)
        std_out, std_err = mafft_cline()
        with open(os.path.join(self.dir, 'aligned.fa'), 'w') as f:
            f.write(std_out)

    # TODO: def _clustal_align():

    def build(self):
        if self.treeTool == 'raxml':
            working_dir = os.getcwd()
            os.chdir(self.dir)
            print("generating ML tree...")
            self._raxml_mltree()
            print("bootstrapping...")
            self._raxml_bootstrap()
            print("bipartitioning....")
            self._raxml_bipartition()
            os.chdir(working_dir)
        elif self.treeTool == 'clustal':
            # self._clustal_mltree()
            # self._clustal_bootstrap()
            self.fatal_error(error.INVALID_SELECTION)
            return
        else:
            self.fatal_error(error.INVALID_SELECTION)
            return

    @staticmethod
    def _raxml_mltree():
        raxml = "raxmlHPC-PTHREADS-SSE3"
        raxml_cline = RaxmlCommandline(cmd=raxml, sequences='aligned.fa', model="GTRCAT", name='T1', threads=3)
        raxml_cline()

    @staticmethod
    def _raxml_bootstrap():
        raxml = "raxmlHPC-PTHREADS-SSE3"
        raxml_cline = RaxmlCommandline(cmd=raxml, sequences='aligned.fa', model="GTRCAT", name='T2', threads=3,
                                       bootstrap_seed="1000", num_replicates="10")
        raxml_cline()

    @staticmethod
    def _raxml_bipartition():
        raxml = "raxmlHPC-PTHREADS-SSE3"
        T1 = 'RAxML_bestTree.T1'
        T2 = 'RAxML_bootstrap.T2'
        raxml_cline = RaxmlCommandline(cmd=raxml, model="GTRCAT", name='nh', algorithm="b",
                                       starting_tree=T1, bipartition_filename=T2, threads=3)
        raxml_cline()

    # TODO: def clustal_build

    def visualize(self):
        print("drawing tree...")
        bipartition2 = os.path.join(self.dir, "RAxML_BipartitionsBranchLabels.nh")
        # Phylo.convert(bipartition, 'newick', bipartition2, 'nexus')
        t = Phylo.read(bipartition2, 'newick')
        t.ladderize()
        Phylo.draw(t, do_show=False)
        pylab.savefig(os.path.join(self.dir, self.name + '.png'))
        pylab.show()


if __name__ == '__main__':
    tree = Tree('testTree', project_accs, 'mafft', 'raxml')
    tree.get_sequences()
    tree.align()
    tree.build()
    tree.visualize()
