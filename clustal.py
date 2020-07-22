# def clustalw_align():
    #     # clustalw must be in your system PATH variable, or add the absolute path location of clustalw binaries as the
    #     # first argument to ClustalwCommandline()
    #     cw2 = "/Library/Clustal/bin/clustalw2"
    #
    #     clustalw_cline = ClustalwCommandline(cw2, infile=in_file)
    #     clustalw_cline.align = True
    #     clustalw_cline.output = options['align_file_type']
    #     clustalw_cline.outfile = 'clustal_aligned.aln'
    #
    #     # execute the commandline object
    #     clustalw_cline()
    #
    #     return 'clustal_aligned.aln'



# def clustalw_tree(in_file, options={'outputtree': 'phylip'}):
#     cw2 = "/Library/Clustal/bin/clustalw2"
#
#     # create clustalw command line script object
#     clustalw_cline = ClustalwCommandline(cw2, infile=in_file)
#     clustalw_cline.tree = True
#     clustalw_cline.outputtree = options['outputtree']
#     clustalw_cline.quiet = True
#
#     # execute the commandline object
#     clustalw_cline()
#
#     if options['outputtree'] == 'phylip':
#         return in_file.split('.')[0] + '.ph'
#     else:
#         return in_file.split('.')[0] + '.tre'
#
#
# def clustalw_bs(in_file, options={'bootstrap': 10, 'seed': 1000, 'outputtree': 'phylip'}):
#     # cw2 = "/home/mnygard/local/bin/clustalw/clustalw2"
#     cw2 = "/Library/Clustal/bin/clustalw2"
#     # create clustalw command line script object
#     clustalw_cline = ClustalwCommandline(cw2, infile=in_file)
#     clustalw_cline.bootstrap = options['bootstrap']
#     clustalw_cline.seed = options['seed']
#     clustalw_cline.bootlabels = 'node'
#     clustalw_cline.outputtree = options['outputtree']
#
#     # execute the commandline object
#     clustalw_cline()
#
#     if options['outputtree'] == 'phylip':
#         return in_file.split('.')[0] + '.phb'
#     else:
#         return in_file.split('.')[0] + '.treb'