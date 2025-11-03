# %%
import sys, os, json

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
        print(d)
        if os.path.isfile(os.path.join(d, 'metadata.json')):
            with open(os.path.join(d, 'metadata.json'),
                    'r') as f:
                content = f.read()
            with open(os.path.join(d, 'metadata.json'),
                    'w') as f:
                f.write(content)
        elif os.path.isfile(os.path.join(d, 'metadata.npy')):
            print('to be fixed for old metadata.npy files')

else:
    print("""

need to provide a valid .xlsx file as argument

""")


# %%
