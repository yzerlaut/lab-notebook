# %%
"""
plots the raw data of the ephys experiment

for the stimulus-averaged data,
assume that you have run:

    generate-epData-4dim-visualStim.py

    to create the temp/ folder with the "epData" objects
"""
import os, sys
import pandas as pd
import numpy as np
import itertools
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
from physion.dataviz.raw import plot as plot_raw

from physion.dataviz.ephys import show_waveforms

# %%
datafolder = os.path.join(os.path.expanduser('~'), 
                    'DATA', 'Sally', 'Npx_WT_prelim_2026')

dataset = scan_folder_for_NWBfiles(datafolder,
                                   for_protocol='4dim')

# %%
# generate all stimulus keys:
all_stimKeys = []
for s,i,c,t,e in itertools.product(\
    ['+','-'], [1,2], ['+','-'], ['+','-'], ['+','-']):
    all_stimKeys.append('s%st%sc%se%s%i' %(s,t,c,e,i))
print(all_stimKeys)
# %%

def get_stimKey_from(data, protocol_id, contrast, radius, index):

    abbrev = ''
    stim_type = data.metadata['Protocol-%i-Stimulus' % (protocol_id+1)]
    if 'natural' in stim_type: 
        abbrev += 's+'
    else: 
        abbrev += 's-'
    if 'VSE' in stim_type: 
        abbrev += 't+'
    else: 
        abbrev += 't-'
    if contrast>0.5: 
        abbrev += 'c+'
    else: 
        abbrev += 'c-'
    if radius>=20.: 
        abbrev += 'e+'
    else: 
        abbrev += 'e-'
    if index==1: 
        abbrev += '2' 
    else: 
        abbrev += '1'
    return abbrev

# %%
def load_epData(filename, stim):

    f = 'temp/%s-%s' % (os.path.basename(filename).replace('.nwb',''),
                        stim+'.npy')
    if os.path.isfile(f):
        return np.load(f, allow_pickle=True).item()
    else:
        print('file "%s" not found ! ' % f)
        return None


epData = load_epData(dataset['files'][0], all_stimKeys[0])
# %%
d['running']>0.1

# %%

def stim_annot(ax, stim,
            xycoords='axes fraction', ha='right',
            loc=(0.29,1.05)):
    title = stim[1::2]+' '+'\n'+stim[::2]
    ax.annotate(title, loc, ha=ha, fontsize=7,
                xycoords=xycoords,
                linespacing=0.6, family='monospace')


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

GOOD_RECS = []

for i, f in enumerate(dataset['files']):
    data = Data(f)
    data.build_pupil()
    data.build_facemotion()
    if hasattr(data, 'pupil') and hasattr(data, 'facemotion') and ('4dim' in data.metadata['protocol']):
        fig, _ = plot_raw(data, tlim=[5, data.tlim[1]], settings=settings)
        fig.suptitle('%i) %s \n % s' % (i, f, data.metadata['protocol']))
        GOOD_RECS.append(f)

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

for i, f in enumerate(GOOD_RECS):
    data = Data(f)
    fig, _ = plot_raw(data, 
                      tlim=[5, data.tlim[1]], settings=settings)
    fig.suptitle('%i) %s \n % s' % (i, f, data.metadata['protocol']))
# %%
from scipy.ndimage import gaussian_filter1d
data = Data(GOOD_RECS[1])
data.build_running()
running = gaussian_filter1d(data.running, 10)
data.build_pupil()
pupil = gaussian_filter1d(data.pupil, 10)
data.build_facemotion()
facemotion = gaussian_filter1d(data.facemotion, 50)

# %%
fig, AX = pt.figure(axes=(1,3), ax_scale=(2.5,0.4),hspace=0.)
pt.set_common_xlims(AX, lims=[0,data.tlim[1]])
for ax, color, t, x in zip(AX, ['tab:red', 'tab:purple', 'tab:blue'],
                        [data.t_pupil, data.t_facemotion, data.t_running],
                        [pupil, facemotion, running]):
    x = gaussian_filter1d(x, 20)
    cond = t>5
    ax.plot(t[cond][::20], x[cond][::20], color=color, lw=1)
pt.set_common_xlims(AX, lims=[-250,data.tlim[1]])
for ax, scale, label in zip(AX, 
                        [50,10,2], ['0.2mm', 'a.u.', '2cm/s ']):
    pt.draw_bar_scales(ax, Ybar=scale, Ybar_label=label, color='k', 
                       Xbar=5*60 if ax==AX[0] else 1e-3,
                       Xbar_label='5min' if ax==AX[0] else '')
ZOOM = [1730, 80]
ZOOM = [600, 60]
ZOOM = [1880, 60]
ZOOM = [2100, 80]
for ax in AX:
    ylim = ax.get_ylim()
    ax.fill_between(ZOOM[0]+np.arange(2)*ZOOM[1], np.ones(2)*ylim[0], np.ones(2)*ylim[1], 
                    color='k', alpha=.2, lw=0)
    ax.set_ylim(ylim)
    ax.axis('off')
pt.save(fig)
# %%

# %%
def build():
    fig, AX = pt.figure(
        axes_extents=[[[1,3]],[[1,2]],[[1,2]],[[1,4]],
                    [[1,1]],[[1,1]],[[1,1]]],
        ax_scale=(3.,0.35), hspace=0)
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
                     lim=[0,11], 
                     color='dimgrey',
                     scale=5, scale_label='5hz'),
         MUA = dict(smoothing=20e-3, 
                     lim=[30,75], 
                     color='darkblue',
                     scale=20, 
                     electrode_average=[15,25],
                     scale_label='20$\\mu$V'),
         LFP = dict(lim=[-.5e3,2.2e3],
                    space=0.6e3,
                    scale=500,
                    scale_label='500$\\mu$V',
                    electrodes=[-4, -3, -2, -1],
                    lw=0.5,
                    color='darkgreen'),
         pupil = dict(lim=[70,200],
                      scale=50,
                      scale_label='0.2mm  ',
                      color='tab:red'),
         whisk = dict(lim=[0,150],
                      scale=200,
                      scale_label='a.u.',
                      color='tab:purple'),
         run = dict(lim=[-1,4.5],
                     scale=2,
                      scale_label='2cm/s',
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

        cond = (t>tlim[0]) & (t<tlim[1]) & (mod<settings['lim'][1])
        AX[key].plot(t[cond][::1],
                mod[cond][::1], 
                lw=1, color=settings['color'])

    # visual stim condition.
    stim_cond = ((data.time_start+data.time_duration)>tlim[0]) &\
                    (data.time_start<tlim[1])

    #### y-scale ####
    for key, settings in zip(
        ['spikes', 'rate', 'MUA', 'LFP', 'pupil', 'whisk', 'run'], 
        [spikes, rate, MUA, LFP, pupil, whisk, run]):

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

        for tstart, duration in zip(data.time_start[stim_cond], 
                                    data.time_duration[stim_cond]):
            AX[key].fill_between([max(tstart,tlim[0]), min(tstart+duration,tlim[1])],
                                settings['lim'][0]*np.ones(2),
                                settings['lim'][1]*np.ones(2),
                                color='red', alpha=.05, lw=0)

    # stim annotation
    for i in np.arange(len(data.time_start))[stim_cond[:,0]]:
        stim_annot(AX['spikes'], 
            get_stimKey_from(data, 
                    data.visual_stim.experiment['protocol_id'][i], 
                    data.visual_stim.experiment['contrast'][i], 
                    data.visual_stim.experiment['radius'][i], 
                    data.visual_stim.experiment['index'][i]),
                loc=(data.time_start[i,0], spikes['lim'][1]),
                xycoords='data', ha='left')
                   
    #####################
    for key in AX:
        AX[key].axis('off')
        AX[key].set_xlim([tlim[0]-0.05*dtlim, tlim[1]])



def prepare_full_view(data):
    data.build_spikes()
    data.build_MUA()
    data.build_LFP()
    data.build_facemotion()
    facemotion = gaussian_filter1d(data.facemotion, 100)
    data.time_start = data.nwbfile.stimulus['time_start_realigned'].data[:]
    data.time_duration = data.nwbfile.stimulus['time_duration'].data[:]
    data.build_visual_stim()

if 1:
    prepare_full_view(data)

if 1:
    fig, AX = build()
    plot(data, AX, **{'tlim':ZOOM[0]+np.arange(2)*ZOOM[1]})


    figs, AXs = [], []
    Settings1 = {
        'tlim': ZOOM[0]+np.arange(2)*ZOOM[1],
        'Tbar':1, 'Tbar_label':'1s',
        'subsampling':20,
    }
    for settings in [Settings1]:
        fig, AX = build()
        prepare_full_view(data)
        plot(data, AX, **settings)
        # figs.append(fig)
        # AXs.append(AX)
pt.save(fig)
# %%
data.build_visual_stim()
data.visual_stim.experiment

# %%

for i in range(16):

    p = get_stimKey_from(data, 
            data.visual_stim.experiment['protocol_id'][i],
            data.visual_stim.experiment['contrast'][i],
            data.visual_stim.experiment['radius'][i],
            data.visual_stim.experiment['index'][i])
    print(p)

# %%
if 1:
    # %%
    import os
    from PIL import Image
    import matplotlib.pylab as plt
    import plot_tools as pt
    import numpy as np

    fig_folder = os.path.join(
            os.path.expanduser('~'), 'Documents',
            'Notebook', 'Projects', 'Sally-PhD',
            'figures', 'stims')

    figs = [int(f.split('_')[0]) for f in os.listdir(fig_folder)]
    figs=np.array(os.listdir(fig_folder))[np.argsort(figs)]

    fig, AX = pt.figure(axes=(6,6),
                        ax_scale=(.8,.5),
                        wspace=0.5,
                        hspace=1.7)

    for i, key, ax in zip(range(len(all_stimKeys)), all_stimKeys, pt.flatten(AX)):
        inset = pt.inset(ax, (0.3,1.,0.6,0.8)) 
        im = Image.open(os.path.join(fig_folder, '%i_%s.png' % (i+1, key)))
        inset.imshow(im)
        inset.axis('off')
        # annotation
        stim_annot(ax, key)
        # 
        # d = load_epData(dataset['files'][2], key)
        d = load_epData(dataset['files'][2], key)
        mod = 'spikes'
        baseline = 0.002
        if d is not None:
            t = np.arange(d[mod].shape[2])*1e-3
            # ax.plot(t,
            ax.fill_between(t[::4],
                    0*t[::4]+baseline,
                gaussian_filter1d(\
                    d[mod][:,:,:].mean(axis=(0,1)),50)[::4]+0.001,
                    color='dimgrey',alpha=1.0,lw=0)
            run = (d['running']>0.1)
            ax.plot(t[::4],
                gaussian_filter1d(\
                    d[mod][run,:,:].mean(axis=(0,1)),40)[::4], lw=0.5,color='#800080')
            ax.plot(t[::4],
                gaussian_filter1d(\
                    d[mod][~run,:,:].mean(axis=(0,1)),30)[::4], lw=0.5, color='#008080')
            ax.axis('off')

    pt.set_common_ylims(AX[:32], lims=[0.0008, 0.016])
    ylim = pt.flatten(AX)[0].get_ylim()
    for i, key, ax in zip(range(len(all_stimKeys)), all_stimKeys, pt.flatten(AX)):
        if 't+' in key:
            ax.fill_between([0,1.5,1.5,5.5,5.5,t[-1]], 
                            np.ones(6)*ylim[0],
                            np.array([0,0,1,1,0,0])*(ylim[1]-ylim[0])+ylim[0],
                    color='r', alpha=0.1,lw=0)
        else:
            ax.fill_between([0,1.5,1.5,3.5,3.5,t[-1]], 
                            np.ones(6)*ylim[0],
                            np.array([0,0,1,1,0,0])*(ylim[1]-ylim[0])+ylim[0],
                    color='r', alpha=0.1,lw=0)

    for ax in pt.flatten(AX[:32]):
        pt.draw_bar_scales(ax, Xbar=1, 
                        # Xbar_label='1s' if ax==AX[0] else '',
                        Ybar=0.005,
                        # Ybar_label='2Hz' if ax==AX[0] else '',
                        loc='top-right')
pt.save(fig, dpi=300)
# %%

epData = load_epData(dataset['files'][4], all_stimKeys[0])
np.sum(epData['running']>0.1)
# %%
if 0:
    data.build_spikeWaveforms()
    fig, _ = show_waveforms(data,
                y_shift_factor=0.5,
                channels_around=4,  
                color='k')

    # %%
    pt.save(fig)
    # %%
