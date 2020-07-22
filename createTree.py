import fileinput


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
