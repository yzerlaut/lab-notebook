# %%
import sys, os
sys.path += ['../physion/src']
from physion.analysis.read_NWB import Data, scan_folder_for_NWBfiles

from physion.notebook.dataset import markdown_table
from physion.notebook.datafile import single_recording_summary

import physion.utils.plot_tools as pt
pt.set_style('dark')

notebook = {
    'data-folder':os.path.expanduser(\
        '~/OneDrive - ICM/Lab-Notebook/Data/'),
    'analysis-report':os.path.expanduser(\
        '~/OneDrive - ICM/Lab-Notebook/Projects/Example.md'),
}

# %%
###################################
###           DATASET           ###
###################################
folder = os.path.expanduser(\
                '~/DATA/physion_Demo-Datasets/SST-WT')
dataset = scan_folder_for_NWBfiles(folder)
# filenames = [\
#     '2023_02_15-13-30-47',
#     '2023_02_15-14-05-01',
#     '2023_02_15-15-10-04',
#     '2024_08_27-10-52-11',
#     '2024_08_27-11-16-53',
#     ]
# dataset = scan_folder_for_NWBfiles(folder, from_filenames=filenames)
markdown_table(dataset, 
                append_to=notebook['analysis-report'])

# %%
for f in dataset['files']:
    single_recording_summary(f, 
            notebook_folder=notebook['data-folder'])
# %%
