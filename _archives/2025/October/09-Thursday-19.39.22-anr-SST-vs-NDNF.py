# %%
import sys, os

import numpy as np
import matplotlib.pylab as plt
from scipy.ndimage import gaussian_filter1d
import plot_tools as pt

sys.path += ['physion/src']
import physion

# %%
NDNF_DATASET = \
    physion.analysis.read_NWB.scan_folder_for_NWBfiles(
        os.path.expanduser('~/DATA/Yann/NDNF-WT-Dec-2022/NWBs'))

# %%
def load_file(filename, dataset='SST'):
    data = physion.analysis.read_NWB.Data(filename)
    data.build_dFoF()
    data.running_speed = data.build_running_speed(specific_time_sampling=data.t_dFoF)
    data.t_running_speed = data.t_dFoF
    data.pupil_diameter = data.build_pupil_diameter(specific_time_sampling=data.t_dFoF)
    data.t_facemotion = data.t_dFoF
    if dataset=='SST':
        ep = physion.analysis.process_NWB.EpisodeData(data, 
                                    protocol_name='luminosity')
        data.t0 = ep.time_start[getattr(ep, 'bg-color')==0.5][0]+10
        data.t1 = data.t0+ep.time_duration[0]-20
        data.grey_screen = (data.t_dFoF>data.t0) &\
                                    (data.t_dFoF<data.t1)
    elif dataset=='NDNF':
        ep = physion.analysis.process_NWB.EpisodeData(data, 
                                    protocol_name='grey-10min')
        data.t0 = ep.time_start[0]+10
        data.t1 = data.t0+ep.time_duration[0]-20
        data.grey_screen = (data.t_dFoF>data.t0) &\
                                    (data.t_dFoF<data.t1)

    return data

data = load_file(NDNF_DATASET['files'][0], 'NDNF')

# %%
SST_DATASET = \
    physion.analysis.read_NWB.scan_folder_for_NWBfiles(
        os.path.expanduser('~/DATA/Taddy/SST-WT/Orient-Tuning/NWBs'))
with_blank= [('blank' in ps)\
                for ps in SST_DATASET['protocols']]

# %%
data = physion.analysis.read_NWB.Data(\
                        SST_DATASET['files'][with_blank][0])
data.build_dFoF()
ep = physion.analysis.process_NWB.EpisodeData(data, 
                                protocol_name='luminosity')
t0 = ep.time_start[getattr(ep, 'bg-color')==0.5][0]

# %%
settings = physion.dataviz.raw.find_default_plot_settings(data,
                                                          with_subsampling=True)
fig, ax = physion.dataviz.raw.plot(data,
                                   tlim=[t0, t0+ep.time_duration[0]],
                                   settings=settings)

# %%
data = physion.analysis.read_NWB.Data(\
                        SST_DATASET['files'][with_blank][7])
data.build_dFoF()
settings = {
    'Locomotion': {'fig_fraction': 0.15, 'subsampling': 10,
                'color': '#1f77b4', 'fig_fraction_start': 0.},
    'Pupil': {'fig_fraction': 0.05, 'subsampling': 10,
                'color': '#d62728', 'fig_fraction_start': 0.15},
    'FaceMotion': {'fig_fraction': 0.05, 'color': 'tab:purple'},
    'CaImaging': {'fig_fraction': 0.75,
                   'subquantity': 'dFoF', 'color': '#2ca02c',
                    'roiIndices': np.arange(data.nROIs), #[:int(data.nROIs/2)],
                    'fig_fraction_start': 0.25},
 
}
ep = physion.analysis.process_NWB.EpisodeData(data, 
                                protocol_name='luminosity')
t0 = ep.time_start[getattr(ep, 'bg-color')==0.5][0]
fig, ax = physion.dataviz.raw.plot(data,
                                   tlim=[t0, t0+ep.time_duration[0]],
                                   settings=settings)

# %%
data = physion.analysis.read_NWB.Data(\
                        SST_DATASET['files'][with_blank][7])
data.build_dFoF()
data.build_running_speed()
data.running_speed = gaussian_filter1d(data.running_speed, 10)
data.build_facemotion()
data.facemotion = gaussian_filter1d(data.facemotion, 2)

settings = {
    'Pupil': {'fig_fraction': 0.1, 'subsampling': 10,
                'color': '#d62728', 'fig_fraction_start': 0.15},
    'FaceMotion': {'fig_fraction': 0.1, 'color': 'tab:purple'},
    'Locomotion': {'fig_fraction': 0.2, 
                   'subsampling': 1, 
                'color': '#1f77b4', 'fig_fraction_start': 0.},
    'CaImaging': {'fig_fraction': 0.6, 'subsampling':3,
                   'subquantity': 'dFoF', 'color': '#2ca02c',
                    'roiIndices': [9,17,10,14,6,8,20],
                    'fig_fraction_start': 0.25},
 
}
ep = physion.analysis.process_NWB.EpisodeData(data, 
                                protocol_name='luminosity')
t0 = ep.time_start[getattr(ep, 'bg-color')==0.5][0]
fig, ax = physion.dataviz.raw.plot(data,
                                   figsize=(3,2.5),
                                   tlim=[700,911],
                                   settings=settings)
# %%

# %%

FINAL = {
    'SST':{'dataset':SST_DATASET['files'][with_blank]},
    'NDNF':{'dataset':NDNF_DATASET['files']},#[np.array([0, 1, 2, 3, 6, 8, 11, 13])]},
         }

for key in ['SST', 'NDNF']:
    running_correls, pupil_correls = [], []

    for f in FINAL[key]['dataset']:
        data = load_file(f, key)
        running_correls.append(\
            [np.corrcoef(data.running_speed[data.grey_screen], 
                    data.dFoF[roi, data.grey_screen])[0,1]\
                        for roi in range(data.nROIs)])
        pupil_correls.append(\
            [np.corrcoef(data.pupil_diameter[data.grey_screen], 
                    data.dFoF[roi, data.grey_screen])[0,1]\
                        for roi in range(data.nROIs)])

    FINAL[key]['running_correls'] = running_correls
    FINAL[key]['pupil_correls'] = pupil_correls

# %%
fig, AX = pt.figure(axes=(1,2), hspace=0.1)
for ax, key, color in zip(AX, ['SST','NDNF'], ['tab:orange','gold']):
    ax.hist(np.concatenate(FINAL[key]['running_correls']), color=color)
    pt.set_plot(ax, 
                xlabel='correl. with run.' if key=='NDNF' else '',
                xticks_labels=None if key=='NDNF' else [],
                ylabel='# of ROIs')
    pt.annotate(ax, 'n=%i ROIs\n(N=%i sessions)' % (\
                    len(np.concatenate(FINAL[key]['running_correls'])),
                        len(FINAL[key]['running_correls'])),
                (1,0.7), va='top')

pt.set_common_xlims(AX)
fig, AX = pt.figure(axes=(1, 2), hspace=0.3)
for ax, key, color in zip(AX, ['SST','NDNF'], ['tab:orange','gold']):
    ax.hist(np.concatenate(FINAL[key]['pupil_correls']), color=color)
    pt.set_plot(ax, 
                xlabel='correl. with pupil' if key=='NDNF' else '',
                xticks_labels=None if key=='NDNF' else [],
                ylabel='# of ROIs')
    pt.annotate(ax, 'n=%i ROIs\n(N=%i sessions)' % (\
                    len(np.concatenate(FINAL[key]['running_correls'])),
                        len(FINAL[key]['running_correls'])),
                (1,0.7), va='top')
pt.set_common_xlims(AX)

# %%
data = load_file(FINAL['NDNF']['dataset'][7], 'NDNF')
data.running_speed = gaussian_filter1d(data.running_speed, 10)
data.pupil_diameter = gaussian_filter1d(data.pupil_diameter, 10)
data.facemotion = gaussian_filter1d(\
    data.build_facemotion(specific_time_sampling=data.t_dFoF), 10)
settings = {
    'Pupil': {'fig_fraction': 0.1, 'color': '#d62728', 'fig_fraction_start': 0.15},
    'FaceMotion': {'fig_fraction': 0.1, 'color': 'tab:purple'},
    'Locomotion': {'fig_fraction': 0.2, 'color': '#1f77b4', 'fig_fraction_start': 0.},
    'CaImaging': {'fig_fraction': 0.6, 'subsampling':3,
                   'subquantity': 'dFoF', 'color': '#2ca02c',
                    'roiIndices': np.arange(data.nROIs)[:50],
                    'fig_fraction_start': 0.25},
 
}
fig, ax = physion.dataviz.raw.plot(data,
                                   figsize=(3,10),
                                   tlim=[data.t0, data.t1],
                                   settings=settings)
# %%
data = physion.analysis.read_NWB.Data(\
                    FINAL['NDNF']['dataset'][13], 'NDNF')
data.build_dFoF()
ep = physion.analysis.process_NWB.EpisodeData(data, 
                                protocol_name='grey-10min')
t0 = ep.time_start[0]
data.build_running_speed()
data.running_speed = 2*np.pi*gaussian_filter1d(data.running_speed, 10)
data.build_pupil_diameter()
data.pupil_diameter = gaussian_filter1d(data.pupil_diameter, 6)
data.build_facemotion()
data.facemotion = gaussian_filter1d(data.facemotion, 2)
settings = {
    'Pupil': {'fig_fraction': 0.15, 'color': '#d62728', 'fig_fraction_start': 0.15},
    'FaceMotion': {'fig_fraction': 0.1, 'color': 'tab:purple'},
    'Locomotion': {'fig_fraction': 0.15, 'color': '#1f77b4', 'fig_fraction_start': 0.},
    'CaImaging': {'fig_fraction': 0.6, 'subsampling':3,
                   'subquantity': 'dFoF', 'color': '#2ca02c',
                    'roiIndices': [4,12,2,27,10,13,49],
                    'fig_fraction_start': 0.25},
 
}
fig, ax = physion.dataviz.raw.plot(data,
                                   figsize=(3,2.5),
                                #    tlim=[data.t0, data.t1],
                                   tlim=[570,800],
                                   settings=settings)
# ax.set_xlim([570,800])
# %%
