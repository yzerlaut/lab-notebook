# %%
import os, sys
import numpy as np

sys.path += ['physion/src']
from physion.analysis.read_NWB import Data,\
    scan_folder_for_NWBfiles

user = 'Taddy'
root_folder = os.path.join(\
    os.path.expanduser('~'),
    'CURATED', user
)

# %%
# get the list of NWB files
DATASET = scan_folder_for_NWBfiles(root_folder)

# %%
with open('%s_TSeries_curated_list.txt' % user, 'w') as f:
    for fn in DATASET['files']:
        data = Data(fn)
        f.write(data.TSeries_folder+'\n')
# %%
