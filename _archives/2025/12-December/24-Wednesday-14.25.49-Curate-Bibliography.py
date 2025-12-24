# %%
import os

from pybtex.database.input import bibtex

parser = bibtex.Parser()

bib_data = parser.parse_file(\
    os.path.expanduser('~/Documents/Library/biblio.bib'))

i=0
for key in bib_data.entries.keys():
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
        pass
        ## NEED TO FIX THIS ##

        # print()
        # print('  problem with the entry:  ')
        # print(bib_data.entries[key])


# %%
