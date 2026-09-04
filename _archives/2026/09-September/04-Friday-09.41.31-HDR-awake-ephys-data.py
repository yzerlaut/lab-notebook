# %%
import os, sys
import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d

sys.path += ['physion/src']

from physion.analysis.read_NWB import Data,\
                    scan_folder_for_NWBfiles 
from physion.analysis.episodes.build import EpisodeData

import physion.utils.plot_tools as pt
from physion.dataviz.episodes.evoked_pattern\
         import plot as plot_evoked_pattern
from physion.dataviz.episodes.trial_average\
    import plot as plot_trial_average

from physion.dataviz.ephys import show_waveforms

# %%
if 0:
    datafolder = os.path.join(os.path.expanduser('~'), 
                        'DATA', 'Sally', 'Npx_WT_prelim_2026')
                        # 'DATA', 'Sally', '2026_06_09')

    dataset = scan_folder_for_NWBfiles(datafolder) 

# %%
filename = os.path.join(os.path.expanduser('~'),
        'DATA/Sally/Npx_WT_prelim_2026/NWBs/2026_07_29-17-36-41.nwb')
data = Data(filename)

# %%
def build():
    fig, AX = pt.figure(
        axes_extents=[[[1,1]],[[1,1]],[[1,1]],[[1,2]],
                       [[1,1]],[[1,1]],[[1,1]]],
        ax_scale=(1.7,0.7), hspace=0)
    return fig,\
        {'spikes':AX[0],
         'rate':AX[1],
         'MUA':AX[2],
         'LFP':AX[3],
         'pupil':AX[4],
         'whisk':AX[5],
         'run':AX[6]}

def plot(data, AX, tlim=[0,10], 
         subsampling=10,
         spikes = dict(ms=0.5,
                      color='dimgrey'),
         rate = dict(smoothing=20e-3, 
                     lim=[0,15], 
                     color='dimgrey',
                     scale=5, scale_label='5hz'),
         MUA = dict(smoothing=20e-3, 
                     lim=[70,100], 
                     color='darkblue',
                     scale=20, 
                     electrode_average=[15,25],
                     scale_label='20$\\mu$V'),
         LFP = dict(lim=[-1e3,9e3],
                    space=2.5e3,
                    scale=1000,
                    scale_label='1mV',
                    electrodes=[8, 12, 16, 20],
                    lw=0.5,
                    color='darkgreen'),
         pupil = dict(lim=[40,200],
                      scale=50,
                      scale_label='0.2mm  ',
                      color='tab:red'),
         whisk = dict(lim=[0,210],
                      scale=0,
                      scale_label='a.u.',
                      color='tab:purple'),
         run = dict(lim=[-1,4.5],
                     scale=2,
                      scale_label='2cm/s',
                      color='tab:blue'),
         Tbar=5, Tbar_label='5s',
         with_annot=True):

    dtlim = tlim[-1]-tlim[0]

    # spikes
    cond = (data.t_spikes>tlim[0]) & (data.t_spikes<tlim[1])
    for i in range(data.spikes.shape[0]):
        scond = (data.spikes[i,cond]==1)
        AX['spikes'].plot(data.t_spikes[cond][scond],
            i+data.spikes[i,cond][scond], 
            'o', ms=spikes['ms'], fillstyle='full',
            markerfacecolor=spikes['color'], markeredgecolor='none')
    AX['spikes'].plot(tlim[0]+np.arange(2)*Tbar, 
                      1.12*data.spikes.shape[0]+np.zeros(2), 'k-')
    AX['spikes'].annotate(Tbar_label,
                          (tlim[0], 1.18*data.spikes.shape[0]))
    if with_annot:
        AX['spikes'].annotate('%i units' % data.spikes.shape[0],\
            (tlim[0]-0.025*dtlim, 0), ha='right', rotation=90)
    spikes['lim'] = [-1, 1.18*data.spikes.shape[0]]
    # rate
    dt = data.t_spikes[1]-data.t_spikes[0]
    fr = gaussian_filter1d(\
        np.sum(data.spikes[:,cond], axis=0)/dt/data.spikes.shape[0], 
        int(rate['smoothing']/dt))
    AX['rate'].fill_between(data.t_spikes[cond][::subsampling],
            0*data.t_spikes[cond][::subsampling], fr[::subsampling], 
            color=spikes['color'], lw=0)

    # MUA
    cond = (data.t_MUA>tlim[0]) & (data.t_MUA<tlim[1])
    dt = data.t_MUA[1]-data.t_MUA[0]
    mua = data.MUA[MUA['electrode_average'][0]:MUA['electrode_average'][1],:].mean(axis=0)

    AX['MUA'].fill_between(data.t_MUA[cond][::subsampling],
            0*data.t_MUA[cond][::subsampling], 
            gaussian_filter1d(mua[cond], int(MUA['smoothing']/dt))[::subsampling], 
            color=MUA['color'], lw=0)

    # LFP
    cond = (data.t_LFP>tlim[0]) & (data.t_LFP<tlim[1])
    dt = data.t_LFP[1]-data.t_LFP[0]
    for e, elec in enumerate(LFP['electrodes']):
        lfp = data.LFP[elec,:]
        AX['LFP'].plot(data.t_LFP[cond][::subsampling],
                LFP['space']*e+lfp[cond][::subsampling], 
                lw=LFP['lw'], color=LFP['color'])

    # Pupil, Whisking & Running
    for key, t, mod, settings in zip(
        ['pupil', 'whisk', 'run'], 
        [data.t_pupil, data.t_facemotion, data.t_running],
        [data.pupil, data.facemotion, data.running],
        [pupil, whisk, run]):

        if key in AX:
            cond = (t>tlim[0]) & (t<tlim[1]) & (mod<settings['lim'][1])
            AX[key].plot(t[cond][::1],
                    mod[cond][::1], 
                    lw=1, color=settings['color'])

    #### y-scale ####
    for key, settings in zip(
        ['spikes', 'rate', 'MUA', 'LFP', 'pupil', 'whisk', 'run'], 
        [spikes, rate, MUA, LFP, pupil, whisk, run]):

        if key in AX:
            AX[key].set_ylim(settings['lim'])

            if with_annot and key!='spikes':
                    AX[key].plot((tlim[0]-0.025*dtlim)*np.ones(2),
                                    -settings['scale']*np.arange(2)+\
                                        settings['lim'][0]+.5*np.diff(settings['lim']),
                                    color=settings['color'])
                    AX[key].annotate(settings['scale_label'],
                        (tlim[0]-0.025*dtlim, settings['lim'][0]+.5*np.diff(settings['lim'])[0]),
                        color=settings['color'], 
                        va='center', ha='right', rotation=90)

                   
    #####################
    for key in AX:
        AX[key].axis('off')
        AX[key].set_xlim([tlim[0]-0.05*dtlim, tlim[1]])

def prepare_full_view(data):
    data.build_spikes()
    data.spikes = data.spikes[25:,:]
    data.build_MUA()
    data.build_LFP()
    data.build_facemotion()
    facemotion = gaussian_filter1d(data.facemotion, 50)
    data.time_start = data.nwbfile.stimulus['time_start_realigned'].data[:]
    data.time_duration = data.nwbfile.stimulus['time_duration'].data[:]
    data.build_visual_stim()

if 1:
    prepare_full_view(data)



ZOOM = [358, 58]
ZOOM2 = [406.1, 2.2]
ZOOM1 = [369.8, 2.5]

if 1:
    fig, AX = build()
    plot(data, AX, 
         **{'tlim':ZOOM[0]+np.arange(2)*ZOOM[1],
            'subsampling':20})
    for key in AX:
        ylim = AX[key].get_ylim()
        for z in [ZOOM1, ZOOM2]:
            AX[key].fill_between([z[0], z[0]+z[1]], 
                                ylim[0]*np.ones(2),
                                ylim[1]*np.ones(2), color='k', lw=0, alpha=.1)



pt.save(fig, fig_name='1.svg')

# %
def build():
    fig, AX = pt.figure(
        axes_extents=[[[1,2]],[[1,2]],[[1,2]],[[1,3]]],
        ax_scale=(1.7,0.7), hspace=0)
    return fig,\
        {'spikes':AX[0],
         'rate':AX[1],
         'MUA':AX[2],
         'LFP':AX[3]}

settings = dict(\
         Tbar=.3, Tbar_label='300ms',
         subsampling=1,
         spikes = dict(ms=1,
                      color='dimgrey'),
         rate = dict(smoothing=15e-3, 
                     lim=[0,30], 
                     color='dimgrey',
                     scale=10, scale_label='5hz'),
         MUA = dict(smoothing=10e-3, 
                     lim=[75, 105], 
                     color='darkblue',
                     scale=20, 
                     electrode_average=[5,25],
                     scale_label='20$\\mu$V'),
         LFP = dict(lim=[-2e3,6e3],
                    space=1.5e3,
                    scale=1000,
                    scale_label='1mV',
                    electrodes=[8, 12, 16, 20],
                    lw=0.5,
                    color='darkgreen')
)

if 1:
    fig, AX = build()
    plot(data, AX, 
         tlim=ZOOM1[0]+np.arange(2)*ZOOM1[1],
         **settings)
    pt.save(fig, fig_name='2.svg')
    fig, AX = build()
    plot(data, AX, 
         tlim=ZOOM2[0]+np.arange(2)*ZOOM2[1],
         **settings)
    pt.save(fig, fig_name='3.svg')

# %%
from physion.dataviz.raw import plot as plot_raw,\
            find_default_plot_settings
settings = find_default_plot_settings(data)
fig, _ = plot_raw(data, 
                  tlim=[360,410],
                  settings=settings)
                        
# %%
settings = {
 'pupil': {'color': '#d62728',
  'fig_fraction': 0.3,
  'subsampling': 10,
  'fig_fraction_start': 0.3},
 'facemotion': {'color': 'purple',
  'fig_fraction': 0.3,
  'subsampling': 10,
  'fig_fraction_start': 0.3},
 'running': {'color': '#1f77b4',
  'fig_fraction': 0.3,
  'subsampling': 10,
  'fig_fraction_start': 0.6}
}


for i, f in enumerate(dataset['files']):
    data = Data(f)
    data.build_pupil()
    data.build_facemotion()
    if hasattr(data, 'pupil') and hasattr(data, 'facemotion'):
        fig, _ = plot_raw(data, tlim=[2, data.tlim[1]], settings=settings)
        fig.suptitle('%i) %s \n % s' % (i, f, data.metadata['protocol']))
    # pt.save(fig)

# %%

def build():
    fig, AX = pt.figure(
        axes_extents=[[[1,3]],[[1,2]],[[1,2]],[[1,4]],
                    [[1,2]],[[1,2]],[[1,2]]],
        ax_scale=(1.8,0.2))
    return fig,\
        {'spikes':AX[0],
         'rate':AX[1],
         'MUA':AX[2],
         'LFP':AX[3],
         'pupil':AX[4],
         'whisk':AX[5],
         'run':AX[6]}

def plot(AX, tlim=[0,10], 
         subsampling=4,
         spikes = dict(ms=0.5,
                      color='k'),
         rate = dict(smoothing=50e-3, 
                     lim=[0,10], 
                     color='k',
                     scale=5, scale_label='5hz'),
         MUA = dict(smoothing=50e-3, 
                     lim=[40,80], 
                     color='darkblue',
                     scale=20, 
                     electrode_average=[10,100],
                     scale_label='20$\mu$V'),
         LFP = dict(lim=[-4e3,13e3],
                    space=4e3,
                    scale=2e3,
                    scale_label='2mV',
                    electrodes=[0, 10, 20, 30],
                    lw=0.5,
                    color='darkgreen'),
         pupil = dict(lim=[0,200],
                      scale=1,
                      scale_label='0.5mm  ',
                      color='tab:red'),
         whisk = dict(lim=[0,142],
                      scale=10,
                      scale_label='a.u.',
                      color='tab:purple'),
         run = dict(lim=[0,5],
                     scale=1,
                      scale_label='1cm/s',
                      color='tab:blue'),
         Tbar=10, Tbar_label='10s',
         with_annot=True):

    dtlim = tlim[-1]-tlim[0]

    # spikes
    cond = (data.t_spikes>tlim[0]) & (data.t_spikes<tlim[1])
    for i in range(data.spikes.shape[0]):
        scond = (data.spikes[i,cond]==1)
        AX['spikes'].plot(data.t_spikes[cond][scond],
            i+data.spikes[i,cond][scond], 
            'o', ms=spikes['ms'], fillstyle='full',
            markerfacecolor=spikes['color'], markeredgecolor='none')
    AX['spikes'].plot(tlim[0]+np.arange(2)*Tbar, 
                      1.12*data.spikes.shape[0]+np.zeros(2), 'k-')
    AX['spikes'].annotate(Tbar_label,
                          (tlim[0], 1.18*data.spikes.shape[0]))
    if with_annot:
        AX['spikes'].annotate('%i units' % data.spikes.shape[0],\
            (tlim[0]-0.025*dtlim, 0), ha='right', rotation=90)

    # rate
    dt = data.t_spikes[1]-data.t_spikes[0]
    fr = gaussian_filter1d(\
        np.sum(data.spikes[:,cond], axis=0)/dt/data.spikes.shape[0], 
        int(rate['smoothing']/dt))
    AX['rate'].fill_between(data.t_spikes[cond][::subsampling],
            0*data.t_spikes[cond][::subsampling], fr[::subsampling], color='k', lw=0)

    # MUA
    cond = (data.t_MUA>tlim[0]) & (data.t_MUA<tlim[1])
    dt = data.t_MUA[1]-data.t_MUA[0]
    mua = data.MUA[MUA['electrode_average'][0]:MUA['electrode_average'][1],:].mean(axis=0)

    AX['MUA'].fill_between(data.t_MUA[cond][::subsampling],
            0*data.t_MUA[cond][::subsampling], 
            gaussian_filter1d(mua[cond], int(MUA['smoothing']/dt))[::subsampling], 
            color=MUA['color'], lw=0)

    # LFP
    cond = (data.t_LFP>tlim[0]) & (data.t_LFP<tlim[1])
    dt = data.t_LFP[1]-data.t_LFP[0]
    for e, elec in enumerate(LFP['electrodes']):
        lfp = data.LFP[elec,:]
        AX['LFP'].plot(data.t_LFP[cond][::subsampling],
                LFP['space']*e+lfp[cond][::subsampling], 
                lw=LFP['lw'], color=LFP['color'])

    # Pupil
    for key, t, mod, settings in zip(
        ['pupil', 'whisk', 'run'], 
        [data.t_pupil, data.t_facemotion, data.t_running],
        [data.pupil, data.facemotion, data.running],
        [pupil, whisk, run]):

        cond = (t>tlim[0]) & (t<tlim[1])
        AX[key].plot(t[cond][::subsampling],
                mod[cond][::subsampling], 
                lw=1, color=settings['color'])

    #### y-scale ####
    for key, settings in zip(
        ['rate', 'MUA', 'LFP', 'pupil', 'whisk', 'run'], 
        [rate, MUA, LFP, pupil, whisk, run]):

        AX[key].set_ylim(settings['lim'])

        if with_annot:
                AX[key].plot((tlim[0]-0.025*dtlim)*np.ones(2),
                                -settings['scale']*np.arange(2)+\
                                    settings['lim'][0]+.5*np.diff(settings['lim']),
                                color=settings['color'])
                AX[key].annotate(settings['scale_label'],
                    (tlim[0]-0.025*dtlim, settings['lim'][0]+.5*np.diff(settings['lim'])),
                    color=settings['color'], 
                    va='center', ha='right', rotation=90)

    #####################
    for key in AX:
        AX[key].axis('off')
        AX[key].set_xlim([tlim[0]-0.05*dtlim, tlim[1]])


figs, AXs = [], []
Settings1 = {
    'tlim':[20,70],
    'subsampling':10,
}
Settings2 = {
    'tlim':[20,22],
    'subsampling':1,
    'Tbar':0.5, 'Tbar_label':'500ms',
    'with_annot':False,
}
for settings in [Settings1]:
    fig, AX = build()
    plot(AX, **settings)
    figs.append(fig)
    AXs.append(AX)

# %%
data.build_spikeWaveforms()
fig, _ = show_waveforms(data,
               y_shift_factor=0.5,
               channels_around=4,  
               color='k')

# %%
pt.save(fig)
# %%
