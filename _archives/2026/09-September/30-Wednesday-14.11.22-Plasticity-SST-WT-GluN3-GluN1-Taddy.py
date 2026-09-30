# %%
# general python modules
import sys, os, pprint, pandas
import numpy as np
import matplotlib.pylab as plt
from scipy import stats

sys.path += ['./physion/src']

from physion.analysis.read_NWB import Data, scan_folder_for_NWBfiles
from physion.analysis.episodes.build import EpisodeData
import physion.utils.plot_tools as pt

iFig = 0
# Fig_Folder = os.path.join('/Volumes/', 'T7 Touch', 'FIGURES_SSTs')

# %% [markdown]
# ## Build the dataset from the NWB files

# %%
PROTOCOLS = ['ff-gratings-8orientation-2contrasts-15repeats']
# PROTOCOLS = ['ff-gratings-8orientation-2contrasts-10repeats']
DATASET = {\
    'WT':scan_folder_for_NWBfiles(os.path.join(os.path.expanduser('~'), 'DATA', 'Taddy', 'SST-WT', 'Orient-Tuning', 'NWBs'),
                                  for_protocols=PROTOCOLS),
    'GluN1KO':scan_folder_for_NWBfiles(os.path.join(os.path.expanduser('~'), 'DATA', 'Taddy', 'SST-cond-GluN1KO', 'Orient-Tuning', 'NWBs'),
                                  for_protocols=PROTOCOLS),
    'GluN3KO':scan_folder_for_NWBfiles(os.path.join(os.path.expanduser('~'), 'DATA', 'Taddy', 'SST-GluN3KO', 'Orient-Tuning', 'NWBs'),
                                  for_protocols=PROTOCOLS),
}

# %%
# -------------------------------------------------- #
# ----   Loop over datafiles               --------- #
# -------------------------------------------------- #

dFoF_parameters = dict(\
        roi_to_neuropil_fluo_inclusion_factor=1.15,
        neuropil_correction_factor = 0.7,
        method_for_F0 = 'sliding_percentile',
        percentile=5., # percent
        sliding_window = 6*60, # seconds
)

def add_single_datafile(filename,
                         summary,
                         intervals):

    data = Data(filename, verbose=False)
    
    data.build_dFoF(**dFoF_parameters, verbose=False)
    data.build_Deconvolved(Tau=1.3)

    protocol = 'ff-gratings-8orientation-2contrasts-15repeats' if\
                ('ff-gratings-8orientation-2contrasts-15repeats' in data.protocols) else\
                'ff-gratings-8orientation-2contrasts-10repeats'

    episodes = EpisodeData(data, 
                           quantities=['Deconvolved'],
                           protocol_id=data.get_protocol_id(protocol_name=protocol))

    for i, i1, i2 in zip(range(10), intervals[:-1], intervals[1:]):
        if len(episodes.Deconvolved[i1:i2:,:,:])>0:
            summary[i].append(\
                    episodes.Deconvolved[i1:i2,:,:].mean(axis=(0,1))
                )

    return episodes.t

# %%
from scipy import stats

intervals = np.linspace(0, 150, 4, dtype=int)

SUMMARY = {}
for key in ['GluN1KO', 'WT', 'GluN3KO']:

    summary = [[] for i in range(len(intervals)-1)]

    for f in DATASET[key]['files']:
        t = add_single_datafile(f, summary, intervals)

    summary = np.array(summary)

    # min-max normalization with respect to first episodes
    min = summary[0,:,:].min(axis=-1)
    max = summary[0,:,:].max(axis=-1)
    for i in range(len(summary)):
        summary[i,:,:]  = ((summary[i,:,:].T-min.T)/(max.T-min.T)).T

    SUMMARY[key] = summary
 
# %%
CASES = ['GluN1KO', 'WT', 'GluN3KO']
COLORS = ['tab:purple', 'darkorange', 'tab:green']

fig, AX = pt.figure(axes=(len(intervals)-1, len(CASES)), 
                    ax_scale=(1.,1.1))

for c, key, color in zip(range(3), CASES, COLORS):

    pt.annotate(AX[c][0], key+' ', (0,1), va='top', ha='right', color=color)
    # AX[c][0].set_ylabel('norm.\n$\Delta$F/F')
    AX[c][0].set_ylabel('norm.\nDeconv.')

    summary = SUMMARY[key]

    for i in range(len(summary)):
        AX[c][i].plot(t, 0*t, 'k:')
        AX[c][i].plot(t, 0*t+1, 'k:')
        pt.plot(t, summary[i,:,:].mean(axis=0),
                stats.sem(summary[i,:,:], axis=0),
                ax=AX[c][i], color=color)
    pt.annotate(AX[c][0], ' N=%i sess.' % summary.shape[1], (0,1), va='top', color=color)
        
for i in range(len(intervals)-1):
    AX[0][i].set_title('repeats [%i,%i]' % (intervals[i], intervals[i+1]))
    AX[2][i].set_xlabel('time (s)')

pt.set_common_ylims(AX, lims=[-0.3, 1.9])

# %%
