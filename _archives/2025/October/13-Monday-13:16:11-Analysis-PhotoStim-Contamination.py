# %%
import numpy as np
import sys, os

# physion
sys.path += [os.path.expanduser('~/work/physion/src')]
import physion

# plot
from physion.utils import plot_tools as pt
# pt.set_style('dark')
pt.set_style('manuscript')

# %%
from physion.dataviz.imaging import show_CaImaging_FOV, get_FOV_image
from physion.analysis.read_NWB import Data, scan_folder_for_NWBfiles

# %%
DATASET = scan_folder_for_NWBfiles(\
    os.path.expanduser(\
        '~/DATA/Sofia/Test-PhotoStim-Contamination/data'))

# %%
data = Data(\
    '/Users/yann/DATA/Sofia/Test-PhotoStim-Contamination/data/2025_09_25-12-22-22.nwb')
_ = show_CaImaging_FOV(data, NL=4)
_ = show_CaImaging_FOV(data, NL=4, 
                       roiIndex = np.arange(data.nROIs))
meanImg, _ = get_FOV_image(data, 'meanImg')

pt.plot(meanImg.mean(axis=1), color='tab:green')

# %%
_ = show_CaImaging_FOV(data, NL=10, roiIndex=12,
                       fig_args=dict(ax_scale=(1.4,2.4)))

# %%
fig, ax = pt.figure(ax_scale=(1.2,1.2))
cmap = pt.get_linear_colormap('lightgreen', 'darkgreen')
for i, f in enumerate(DATASET['files']):
    print(f)
    data = Data(f)
    data.build_dFoF()
    # _ = show_CaImaging_FOV(data, NL=4)
    meanImg, _ = get_FOV_image(data, 'meanImg')
    ax.plot(meanImg.mean(axis=1),
            color=cmap(i/len(DATASET['files'])))
pt.set_plot(ax, 
            yscale='log',
            xlabel='vertical pixels', ylabel='mean Img fluo.')
pt.bar_legend(ax, 
              label='incr. power',
              colormap=cmap)
# %%
fig, ax = pt.figure(ax_scale=(1.2,1.2))
f = DATASET['files'][-1]
data = Data(f)
# data.build_neuropil()
data.build_dFoF(neuropil_correction_factor=1.0)
roiIndices = np.arange(data.nROIs)
# roiIndices = [0,11,24] 
_ = show_CaImaging_FOV(data, NL=4, 
                       with_ROI_annotation=True,
                       roiIndex=roiIndices)
_ = show_CaImaging_FOV(data, NL=4)
meanImg, _ = get_FOV_image(data, 'meanImg')
ax.plot(meanImg.mean(axis=1),
        color=cmap(i/len(DATASET['files'])))
pt.set_plot(ax, 
            # yscale='log',
            title='(max. LED power)',
            xlabel='vertical pixels', ylabel='mean Img fluo.')
# %%
fig, AX = pt.figure((3,len(roiIndices)), ax_scale=(1.2,.8), wspace=0.6)

cond = data.t_dFoF>10
data.build_dFoF(neuropil_correction_factor=0.7)
for i, roi in enumerate(roiIndices):
    pt.annotate(AX[i][0], 'ROI #%i' % (1+roi), (0,1))
    AX[i][0].plot(data.t_dFoF[cond],
                  data.neuropil[roi,:][cond],
                  color='tab:red')
    AX[i][0].plot(data.t_dFoF[cond], 
                  data.rawFluo[roi,:][cond],
                  color='tab:green')
    pt.set_plot(AX[i][0], 
                xticks_labels=None if i==2 else [],
                xlabel='time (s)' if i==2 else '')
    AX[i][1].plot(data.t_dFoF[cond],
                  data.dFoF[roi,:][cond],
                  color='tab:green')
    pt.set_plot(AX[i][1], ylabel='$\Delta$F/F',
                xticks_labels=None if i==2 else [],
                xlabel='time (s)' if i==2 else '')
pt.annotate(AX[0][0], 'ROI fluo.   \n', (1,1), color='tab:green', ha='right')
pt.annotate(AX[0][0], 'neuropil   ', (1,1), color='tab:red', ha='right')
pt.annotate(AX[0][1], 'neuropil-subst.=0.7', (1,1), color='tab:green', ha='right')

data.build_dFoF(neuropil_correction_factor=1.0)
for i, roi in enumerate(roiIndices):
    AX[i][2].plot(data.t_dFoF[cond],
                  data.dFoF[roi,:][cond],
                  color='tab:green')
    pt.set_plot(AX[i][2], ylabel='$\Delta$F/F',
                xticks_labels=None if i==2 else [],
                xlabel='time (s)' if i==2 else '')
pt.annotate(AX[0][2], 'neuropil-subst.=1.0', (1,1), color='tab:green', ha='right')

# %%
from physion.analysis.process_NWB import EpisodeData
Ep = EpisodeData(data,
                 protocol_id=0,
                 quantities=['dFoF'])
# %%
from scipy import stats

def plot_effect(Ep, data,
                roi=None,
                title=''):

    episodes = np.arange(len(Ep.time_start))
    blank_cond = (episodes%2==0)
    stim_cond = (episodes%2==1)

    fig, AX = pt.figure(\
        ax_scale=(0.9,0.95),
        axes=(len(Ep.varied_parameters['contrast']),1),
        wspace=0.2, hspace=0.5, top=1.5)

    fig.suptitle(title)

    if roi is None:
        dFoF = Ep.dFoF.mean(axis=1)
    else:
        dFoF = Ep.dFoF[:,roi,:]

    for i, c in enumerate(Ep.varied_parameters['contrast']):

        c_cond = Ep.find_episode_cond('contrast', value=c)

        if i%2==0:
            pt.plot(Ep.t, dFoF[c_cond & blank_cond,:].mean(axis=0),
                    stats.sem(dFoF[c_cond & blank_cond,:], axis=0),
                    ax=AX[i])
            pt.annotate(AX[i], 'blank', (1,1), ha='right', va='top')
        else:
            pt.plot(Ep.t, dFoF[c_cond & stim_cond,:].mean(axis=0),
                    stats.sem(dFoF[c_cond & stim_cond,:], axis=0),
                    ax=AX[i])
            pt.annotate(AX[i], 'stim', (1,1), ha='right', va='top')
        pt.annotate(AX[i], 'c=%.2f' % c, (0.5, 0), va='top', ha='center')

    pt.set_common_ylims(AX)
    y0, y1 = AX[0].get_ylim()
    for i, ax in enumerate(AX):
        # visual stim
        ax.fill_between([0,1],y0*np.ones(2),y1*np.ones(2), alpha=.2, lw=0)
        ax.axis('off')
        # photo-stim
        if i%2==1:
            ax.fill_between([-0.5,1.5],y0*np.ones(2),y1*np.ones(2), 
                                color='tab:blue', alpha=.3, lw=0)

    pt.draw_bar_scales(AX[0],
                    Ybar=0.2, Ybar_label='0.2$\\Delta$F/F',
                    Xbar=1, Xbar_label='1s')
    
    return fig
#
# %%

for NEUROPIL_FACTOR in [0.7, 1.0]:
    for f in DATASET['files'][-4:-2]:
        data = Data(f)
        data.build_dFoF(neuropil_correction_factor=NEUROPIL_FACTOR)
        Ep = EpisodeData(data, protocol_id=0, quantities=['dFoF'])
        plot_effect(Ep, data,
                    title='%s, **ALL ROIs (mean dFoF) **\n' % data.filename+\
                        'neuropil-substraction-factor=%.2f' % NEUROPIL_FACTOR)
# %%
NEUROPIL_FACTOR = 0.7
f = DATASET['files'][-1]

data = Data(f)
data.build_dFoF(neuropil_correction_factor=NEUROPIL_FACTOR)
Ep = EpisodeData(data, protocol_id=0, quantities=['dFoF'])
for roi in range(data.nROIs):
    plot_effect(Ep, data, roi=roi,
                title='%s, ROI #%i **\n' % (data.filename, roi)+\
                    'neuropil-substraction-factor=%.2f' % NEUROPIL_FACTOR)

# %% [markdown]
# # Looking at the neuropil and fluorescence time course

# %%
# %%
from scipy import stats

def plot_neuropil_vs_fluo(Ep, data, 
                          roi=None,
                          title=''):

    episodes = np.arange(len(Ep.time_start))
    blank_cond = (episodes%2==0)
    stim_cond = (episodes%2==1)

    fig, AX = pt.figure(\
        ax_scale=(0.9,0.95),
        axes=(len(Ep.varied_parameters['contrast']),1),
        wspace=0.2, hspace=0.5, top=1.5)

    fig.suptitle(title)

    if roi is None:
        rawFluo = Ep.rawFluo.mean(axis=1)
        neuropil = Ep.neuropil.mean(axis=1)
    else:
        rawFluo = Ep.rawFluo[:,roi,:]
        neuropil = Ep.neuropil[:,roi,:]

    # baseline pre-level
    # rawFluo -= rawFluo[:,Ep.t<0].mean(axis=1)
    # neuropil -= neuropil[:,Ep.t<0].mean(axis=1)
    rawFluo = np.transpose(rawFluo.T-rawFluo[:,Ep.t<0].T.mean(axis=0))
    neuropil = np.transpose(neuropil.T-neuropil[:,Ep.t<0].T.mean(axis=0))

    for i, c in enumerate(Ep.varied_parameters['contrast']):

        c_cond = Ep.find_episode_cond('contrast', value=c)

        if i%2==0:
            pt.plot(Ep.t, rawFluo[c_cond & blank_cond,:].mean(axis=0),
                    ax=AX[i], no_set=True, color='tab:green')
            pt.plot(Ep.t, neuropil[c_cond & blank_cond,:].mean(axis=0),
                    ax=AX[i], no_set=True, color='tab:red')
            pt.annotate(AX[i], 'blank', (1,1), ha='right', va='top')
        else:
            pt.plot(Ep.t, rawFluo[c_cond & stim_cond,:].mean(axis=0),
                    ax=AX[i], color='tab:green', no_set=True)
            pt.plot(Ep.t, neuropil[c_cond & stim_cond,:].mean(axis=0),
                    ax=AX[i], color='tab:red', no_set=True)
            pt.annotate(AX[i], 'stim', (1,1), ha='right', va='top')
        pt.annotate(AX[i], 'c=%.2f' % c, (0.5, 0), va='top', ha='center')

    pt.set_common_ylims(AX)
    y0, y1 = AX[0].get_ylim()
    for i, ax in enumerate(AX):
        # visual stim
        ax.fill_between([0,1],y0*np.ones(2),y1*np.ones(2), alpha=.2, lw=0)
        ax.axis('off')
        # photo-stim
        if i%2==1:
            ax.fill_between([-0.5,1.5],y0*np.ones(2),y1*np.ones(2), 
                                color='tab:blue', alpha=.3, lw=0)

    pt.annotate(AX[3], 'neuropil ', (0,1), ha='right', color='tab:red')
    pt.annotate(AX[3], ' ROI fluo', (0,1), ha='left', color='tab:green')
    pt.draw_bar_scales(AX[0],
                    # Ybar=0.2, Ybar_label='0.2$\\Delta$F/F',
                    Xbar=1, Xbar_label='1s')
    
    return fig

f = DATASET['files'][-4]

data = Data(f)
data.build_rawFluo()
data.build_neuropil()
Ep = EpisodeData(data, protocol_id=0, 
                 quantities=['rawFluo', 'neuropil'])
# for roi in range(data.nROIs):
#     plot_neuropil_vs_fluo(Ep, data, roi,
#                 title='%s, ROI #%i' % (data.filename, roi+1))

_ = plot_neuropil_vs_fluo(Ep, data, 
            title='%s, mean over all ROIs' % data.filename)
#
# %%
_ = show_CaImaging_FOV(data, NL=4, 
                       with_ROI_annotation=True,
                       roiIndex=np.arange(data.nROIs))
# %%

