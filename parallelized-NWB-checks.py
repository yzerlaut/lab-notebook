# %%
import sys, os
sys.path += ['physion/src']
from physion.analysis.read_NWB import Data, scan_folder_for_NWBfiles

from physion.notebook.dataset import markdown_table
from physion.notebook.datafile import single_recording_summary
import multiprocessing as mp

import physion.utils.plot_tools as pt
pt.set_style('dark')

# %%
root_folder = os.path.expanduser('~/CURATED/Cibele')
folders = [f for f in os.listdir(root_folder) if 'V1' in f ]

nb_path = os.path.expanduser(\
    # '~/Library/CloudStorage/OneDrive-ICM/Lab-Notebook/Projects/Cibele-PhD/alignement_checks')
    '~/Documents/Lab-Notebook/Projects/alignement_checks')
os.makedirs(os.path.join(nb_path, 'figures'), exist_ok=True)

# %%


def func(filename):
    fig = pt.plt.figure(figsize=(7,2))
    AX = [pt.inset(fig)]
    return fig, AX

fig = func('')

# %%

if 1:
    for folder in folders:
        dataset = scan_folder_for_NWBfiles(\
                        os.path.join(root_folder, folder, 'NWBs'),
                        add_filenames_on_script=False)
        text = ''
        for fn in dataset['files']:
            ff = os.path.basename(fn).replace('.nwb', '')
            text += """

    ## %s
    ![](figures/%s.svg) 
    - [ ] keep as is
    - [ ] remove
    - [ ] realign using photodiode 
        - [ ] **reverse**

    """ % (ff, ff)

        with open(os.path.join(nb_path, '%s.md' % folder), 'w') as f:
            f.write(text)
        

# %%
def plot_and_save(fn):
    pt.plt.switch_backend('Agg') # no GUI in worker processes
    fig, AX = func(fn)
    fig.savefig(os.path.join(nb_path, 'figures', os.path.basename(fn).replace('.nwb','.svg')))
    pt.plt.close(fig)
    return fn

if 1:
    filenames = []
    for folder in folders:
        dataset = scan_folder_for_NWBfiles(\
                        os.path.join(root_folder, folder, 'NWBs'),
                        add_filenames_on_script=False)
        filenames += list(dataset['files'])

    n_procs = max(1, int(0.8*mp.cpu_count()))
    # 'fork' so that functions defined in interactive cells are available to workers
    with mp.get_context('fork').Pool(n_procs) as pool:
        for fn in pool.imap_unordered(plot_and_save, filenames):
            print('done:', os.path.basename(fn))

# %%
