# %%
import sys, os
import numpy as np

sys.path += ['physion/src']
from physion.analysis.read_NWB import Data, scan_folder_for_NWBfiles
from physion.analysis.episodes.build import EpisodeData

from physion.notebook.dataset import markdown_table
from physion.notebook.datafile import single_recording_summary
import multiprocessing as mp

import physion.utils.plot_tools as pt
pt.set_style('dark')
import matplotlib.pylab as plt


# %%
root_folder = os.path.expanduser('~/CURATED/Cibele')
folders = [f for f in os.listdir(root_folder) if 'V1' in f ]

nb_path = os.path.expanduser(\
    # '~/Library/CloudStorage/OneDrive-ICM/Lab-Notebook/Projects/Cibele-PhD/alignement_checks')
    '~/Documents/Lab-Notebook/Projects/alignement_checks')
os.makedirs(os.path.join(nb_path, 'figures'), exist_ok=True)

# %%


#%%
def func(filename):

    #build
    data = Data(filename, verbose=False)
    data.build_rawFluo()
    quantities = ['rawFluo']

    if data.has_photodiode():
        data.build_photodiode()
        quantities.append('photodiode')

    Episodes = EpisodeData(data,
                            quantities=quantities,
                            protocol_name = data.protocols[0],
                            verbose=False)

    Episodes.rawFluo = np.mean(Episodes.rawFluo, axis = 1)
    N_ep = Episodes.rawFluo.shape[0]

    #compute values of interest
    period_evoked = []
    for quantity in quantities :
        val = getattr(Episodes, quantity)

        for i in range(3):
            period_start = int((i/3) * N_ep)
            period_stop = int(((i+1)/3)*N_ep)
            period_evoked.append(np.mean(val[period_start:period_stop, :], axis = 0))

    #plot

    mosaic = "ABC"
    fig = plt.figure(layout="constrained", figsize = (6,1.5))

    ax_dict = fig.subplot_mosaic(mosaic)
    labels = ['1', '2', '3']
    for i in range(3):
        ax_dict["A"].plot(Episodes.t, period_evoked[i]/np.max(period_evoked[i]), label = labels[i])
    ax_dict["A"].set_xlabel('time')
    ax_dict["A"].set_ylabel('norm mean rawFluo')
    ax_dict["A"].legend(frameon=False)

    if data.has_photodiode():
        for i in range(3,6):
            ax_dict["B"].plot(Episodes.t, period_evoked[i])

        ax_dict["B"].set_xlabel('time')
        ax_dict["B"].set_ylabel('mean Photodiode')

        mask_first_min = [data.t_photodiode <= 60][0]
        ax_dict["C"].plot(data.t_photodiode[mask_first_min], data.photodiode[mask_first_min])
        ax_dict["C"].set_xlabel('time')
        ax_dict["C"].set_ylabel('Photodiode')
    else :
        ax_dict["B"].annotate(text = 'no photodiode', xy = (0.5,0.5), fontsize = 15)
        ax_dict["B"].axis("off")
        ax_dict["C"].axis("off")

    return fig

# %%
# def func(filename):
#     fig = pt.plt.figure(figsize=(4,1.5))
#     AX = [pt.inset(fig)]
#     return fig
# fig = func('')

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
- [ ] keep until:
- [ ] remove
- [ ] realign using photodiode 
    - [ ] **reverse**

""" % (ff, ff)

        with open(os.path.join(nb_path, '%s.md' % folder), 'w') as f:
            f.write(text)
        

# %%
# func(dataset['files'][0])
# %%
def plot_and_save(fn):
    pt.plt.switch_backend('Agg') # no GUI in worker processes
    fig = func(fn)
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
