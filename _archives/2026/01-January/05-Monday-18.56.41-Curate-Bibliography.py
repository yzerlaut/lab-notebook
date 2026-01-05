# %%
"""
Rename Keys
"""
import os

from pybtex.database.input import bibtex

Path = os.path.expanduser('~/Documents/Notebook/Library')

parser = bibtex.Parser()


bib_data = parser.parse_file(os.path.join(Path, 'biblio.bib'))

pdf_files = [f for f in os.listdir(Path) if '.pdf' in f]

pdfs_in_bib = []
for key in bib_data.entries.keys():
    if 'file' in bib_data.entries[key].fields:
        fn = bib_data.entries[key].fields['file'].replace(':PDF','').replace(':','').split(';')[0]
        pdfs_in_bib.append(fn)

to_move = []
for p in pdf_files:
    if p not in pdfs_in_bib:
        to_move.append(p)

print(len(bib_data.entries))
print(len(pdfs_in_bib))
print(len(to_move))

# %%
"""
with open(\
    os.path.expanduser('~/Documents/Notebook/Library/biblio.bib'), 'r') as f:
    text = f.read()

i=0

    try:

        name = bib_data.entries[key].persons['author'][0]
        year = bib_data.entries[key].fields['year']

        good_key = '%s%s' % (str(name).split(',')[0], year)
        # some reformating, old -> new
        for o, n in zip(\
            ['-',' ','à', 'ñ', 'á', 'č', 'ö', 'ă', 'ó', 'í', '{','}','\\','\'','\"','é','ć'],
            ['', '', 'a', 'n', 'a', 'c', 'oe', 'a', 'o', 'i', '', '', '',  '',  '',  'e','c']):
            good_key = good_key.replace(o, n)
        for o, n in zip(\
            ['ä', 'ü', 'ò', 'ç', '^', '`','ø'],
            ['ae','ue','o', 'c', 'o', '', 'o']):
            good_key = good_key.replace(o, n)

        text = text.replace(key, good_key)

        if 'file' in bib_data.entries[key] .fields:

            fn = bib_data.entries[key].fields['file'].replace(':PDF','').replace(':','')

            if os.path.isfile(os.path.join(root_folder, fn)):

                shutil.move(os.path.join(root_folder, fn),
                            os.path.join(root_folder, "%s.pdf" % good_key))


        if good_key not in key:
            i+=1
            if good_key not in bib_data.entries: 
                print(i, ')  ', key, good_key, ' [ok]')
                print()
            else:
                print(i, ')  ', key, good_key, ' [XX]')
                print(bib_data.entries[key])
                print()

        # if 'author' in bib_data.entries[key].persons:
            # print(key)

    except BaseException as be:
        # pass
        ## NEED TO FIX THIS ##

        print()
        print(be)
        print('  problem with the entry:  ')
        print(bib_data.entries[key])

with open(\
    os.path.expanduser('~/Documents/Notebook/Library/biblio.bib'), 'w') as f:
    f.write(text)

# %%
"""
