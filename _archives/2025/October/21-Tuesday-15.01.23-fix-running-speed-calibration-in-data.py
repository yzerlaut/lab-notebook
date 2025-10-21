# %%
import sys, os, json, pprint

sys.path += ['physion/src']
import physion

# %%

DataTable = sys.argv[-1] # 

# for testing:
# DataTable = os.path.expanduser(\
    # '~/CURATED/Cibele/PV-cells_WT_Adult_V1/DataTable.xlsx')

if '.xlsx' in DataTable:

    dataset, _, _ = \
        physion.assembling.dataset.read_spreadsheet(DataTable)

    text_replace = {\
        '"roto-encoder-value-per-rotation": -25300.0':\
            '"roto-encoder-value-per-rotation": -4026.6',
        '"roto-encoder-value-per-rotation": --12563.0':\
            '"roto-encoder-value-per-rotation": -4026.6',
        }

    for d in dataset['datafolder']:

        print(' - loading: ', d)

        if os.path.isfile(os.path.join(d, 'metadata.json')):

            # load
            with open(os.path.join(d, 'metadata.json'),
                    'r') as f:
                content = f.read()

            # print(' --- JSON --- ')
            # print(content)

            # replace 
            for key in text_replace:

                if len(content.split(key))>1:
                    print('   [ok] replacing value in: %s ' % os.path.join(d, 'metadata.json'))
                    content = content.replace(key, text_replace[key])
            
            # rewrite
            with open(os.path.join(d, 'metadata.json'),
                    'w') as f:
                f.write(content)

        elif os.path.isfile(os.path.join(d, 'metadata.npy')):

            # load
            metadata = np.load(os.path.join(d, 'metadata.npy'), 
                               allow_pickle=True).item()

            # print(' --- NPY --- ')
            # pprint.pprint(metadata)
            if metadata["roto-encoder-value-per-rotation"]==-25300.0:
                print('   [ok] replacing value in: %s ' % os.path.join(d, 'metadata.npy'))
                metadata["roto-encoder-value-per-rotation"]=-4026.6

            if metadata["roto-encoder-value-per-rotation"]==-12563.0:
                print('   [ok] replacing value in: %s ' % os.path.join(d, 'metadata.npy'))
                metadata["roto-encoder-value-per-rotation"]=-1999.5

            np.save(os.path.join(d, 'metadata.npy'), 
                    metadata)

else:
    print("""

need to provide a valid .xlsx file as argument

""")


# %%
