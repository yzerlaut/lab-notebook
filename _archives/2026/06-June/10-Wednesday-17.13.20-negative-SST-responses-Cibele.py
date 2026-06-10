# %%
# first run the new python analysis/Contrast-Dataset.py to have the deconvolved responses

import os, sys

folders = [
    "SST-cells_WT_Adult_V1",
]
base_path = os.path.expanduser('~/CURATED/Cibele/')
summary_folder = os.path.join(os.path.expanduser('~'), 
                              'CURATED', 'Cibele', 'summary') 


sys.path += ['./physion/src']

from physion.analysis.protocols.contrast_sensitivity\
        import plot_contrast_sensitivity,\
                plot_contrast_responsiveness

fig, ax = plot_contrast_sensitivity(\
                        ['Deconvolved_SST-cells_WT_Adult_V1_angle-90.0'], 
                        path=summary_folder)
ax.set_ylabel('$\delta$ Deconvolved')
fig, ax = plot_contrast_responsiveness(\
    ['Deconvolved_SST-cells_WT_Adult_V1_angle-90.0'],
                        sign='positive',
                        path=summary_folder)
fig, ax = plot_contrast_responsiveness(\
    ['Deconvolved_SST-cells_WT_Adult_V1_angle-0.0'],
                        sign='negative',
                        path=summary_folder)


# %%
# find all negatively modulated neurons
import numpy as np
summary = np.load(
    os.path.join(summary_folder, 
        'Sensitivities_Deconvolved_SST-cells_WT_Adult_V1_angle-90.0.npy'),
        allow_pickle=True) #.item()
files, negROIs = [], []
for sum in summary:
    iS = np.flatnonzero(np.sum(sum['significant_neg'],axis=1))
    files.append(sum['datafile'])
    negROIs.append(iS)
# %%
from physion.analysis.read_NWB import Data
from physion.analysis.episodes.build import EpisodeData
from physion.dataviz.episodes.trial_average import plot as plot_trial_average
from physion.utils import plot_tools as pt

dFoF_params = dict(\
        roi_to_neuropil_fluo_inclusion_factor=1.15,
        neuropil_correction_factor = 0.7,
        method_for_F0 = 'sliding_percentile',
        percentile=5., # percent
        sliding_window = 5*60, # seconds
)

stat_test_props = dict(interval_pre=[-1,-0.2], 
                       interval_post=[0.2,1],
                       test='ttest',
                       sign='negative')

def cell_sensitivity_example_fig(filename,
                                 angle=0,
                                 quantity='Deconvolved',
                                response_significance_threshold = 0.05,
                                Nsamples = 10, # how many cells we show
                                picked_rois=None,
                                 color='k',
                                seed=10):
    
    np.random.seed(seed)
    
    data = Data(filename)
    data.build_dFoF(**dFoF_params)
    if quantity=='Deconvolved':
        data.build_Deconvolved()

    data.init_visual_stim()

    EPISODES = EpisodeData(data,
                           quantities=[quantity],
                           protocol_id=np.flatnonzero(['8contrasts' in p for p in data.protocols]),
                        #    with_visual_stim=True,
                           verbose=True)
    EPISODES.init_visual_stim(data) 

    if picked_rois is None:
        picked_rois = np.random.choice(np.arange(data.nROIs), 
                        min([Nsamples, data.nROIs]), replace=False)
    else:
        picked_rois = np.random.choice(picked_rois,
                        min([Nsamples, len(picked_rois)]), replace=False)


    fig, AX = pt.plt.subplots(len(picked_rois), len(EPISODES.varied_parameters['contrast']), 
                          figsize=(7,7*len(picked_rois)/Nsamples))
    pt.plt.subplots_adjust(right=0.75, left=0.1, top=0.94, bottom=0.05, wspace=0.1, hspace=0.8)
    
    for Ax in AX:
        for ax in Ax:
            ax.axis('off')


    for i, r in enumerate(picked_rois):

        # SHOW trial-average
        plot_trial_average(EPISODES,
                           condition=(EPISODES.angle==angle),
                           column_key='contrast',
                           color=color,
                           quantity=quantity,
                           smoothing=100,
                           Ybar=1. if quantity=='dFoF' else 0.01,
                           Ybar_label='1dF/F' if quantity=='dFoF' else None,
                           Xbar=1., Xbar_label='1s',
                           roiIndex=r,
                           with_std=False,
                           with_stat_test=True,
                           stat_test_props=stat_test_props,
                           with_screen_inset=False,
                           AX=[AX[i]], no_set=False)
        AX[i][0].annotate('roi #%i  ' % (r+1), (0,0), ha='right', xycoords='axes fraction')

        # SHOW summary angle dependence
        inset = pt.inset(AX[i][-1], (2.2, 0.2, 1.2, 0.8))

        contrasts, y, sy, responsive_contrasts = [], [], [], []
        responsive = False

        for c, contrast in enumerate(EPISODES.varied_parameters['contrast']):

            stats = EPISODES.stat_test_for_evoked_responses(episode_cond=\
                                            EPISODES.find_episode_cond(key=['angle', 'contrast'],
                                                                       value=[angle, contrast]),
                                                            response_args=dict(quantity=quantity, roiIndex=r),
                                                            **stat_test_props)

            contrasts.append(contrast)
            y.append(np.mean(stats.y-stats.x))    # means "post-pre"
            sy.append(np.std(stats.y-stats.x))    # std "post-pre"

            if stats.significant(threshold=response_significance_threshold):
                responsive = True
                responsive_contrasts.append(contrast)

        pt.scatter(contrasts, np.array(y), 
                   sy=np.array(sy), ax=inset, ms=1, lw=1, color=color)
        inset.plot(contrasts, 0*np.array(contrasts), 'k:', lw=0.5)
        inset.set_ylabel('$\\delta$ Deconv.   ', fontsize=7)
        inset.set_xticks([0,1])
        #inset.set_xticklabels(['%i'%a if (i%2==0) else '' for i, a in enumerate(contrasts)], fontsize=7)
    inset.set_xlabel('contrast', fontsize=7)

    fig.suptitle('session %s' % os.path.basename(filename))

    return fig

# %%
# first session example
fig = cell_sensitivity_example_fig(files[0], seed=5)
# second session example
fig = cell_sensitivity_example_fig(files[-3], seed=5)

# %%
for f, rois in zip(files, negROIs):
    if len(rois)>1:
        fig = cell_sensitivity_example_fig(f, seed=3, picked_rois=rois)
        fig.suptitle('session #%s' % os.path.basename(f))
    else:
        print(os.path.basename(f), rois)

# %%
from scipy.ndimage import gaussian_filter1d

def load_data(filename):
    data = Data(filename)
    data.build_dFoF(**dFoF_params)
    data.build_Deconvolved()
    pupil = data.build_pupil_diameter(specific_time_sampling=data.t_dFoF)
    running = data.build_running_speed(specific_time_sampling=data.t_dFoF)
    data.init_visual_stim()
    return data, pupil, running


def build_fig(rois):
    axes_extents = [[[1,2]] for roi in rois]
    axes_extents += [[[1,3]] for i in range(2)]
    axes_extents += [[[1,2]]]
    return pt.figure(axes_extents=axes_extents, 
                        ax_scale=(2.5,.3), hspace=0, top=4)
def scale(x):
    return (x-x.min())/(x.max()-x.min())

def show_raw(filename,
            rois = [21, 14, 0, 1, 2, 4],
            smoothing = 2,
            tlim = [20, 120],
            color='tab:orange'):

    data, pupil, running = load_data(filename)

    fig, AX = build_fig(rois)

    cond = (data.t_dFoF>tlim[0]) & (data.t_dFoF<tlim[1])
    for r, roi in enumerate(rois):

        deconv = gaussian_filter1d(data.Deconvolved[roi,:][cond], smoothing)
        AX[r].fill_between(data.t_dFoF[cond], 0*data.t_dFoF[cond],
                        scale(deconv), color=color, alpha=.7)

        fluo = gaussian_filter1d(data.dFoF[roi,:][cond], smoothing)
        AX[r].plot(data.t_dFoF[cond], scale(fluo), 
                lw=0.5, color='tab:green', alpha=.5)
        pt.annotate(AX[r], 'roi #%i ' % (1+roi), (0., 0.5), ha='right', va='center')

    AX[-3].plot(data.t_dFoF[cond], scale(pupil[cond]), lw=1, color='tab:red')
    pt.annotate(AX[-3], 'pupil ', (0., 0.5), ha='right', va='center', color='tab:red')

    AX[-2].plot(data.t_dFoF[cond], scale(running[cond]), lw=1, color='tab:blue')
    pt.annotate(AX[-2], 'running ', (0., 0.5), ha='right', va='center', color='tab:blue')

    pt.annotate(AX[-1], 'contrast ', (0., 0.5), ha='right', va='center', color='k')

    for ax in AX:
        ax.set_xlim(tlim)
        ax.axis('off')

        cond = (data.visual_stim.experiment['time_start']>tlim[0]) &\
        (data.visual_stim.experiment['time_stop']<tlim[1])

        for start, stop, contrast in zip(\
            data.visual_stim.experiment['time_start'][cond],
            data.visual_stim.experiment['time_stop'][cond],
            np.array(data.visual_stim.experiment['contrast'])[cond]):
            ax.fill_between([start, stop], 
                            [0,0], [1.1,1.1],
                            alpha=.1, color='k', lw=0)
            if ax==AX[-1]:
                ax.fill_between([start, stop], 
                                [0,0], [contrast, contrast],
                                color='k', lw=0)
        ax.set_ylim([0,1.1])
    fig.suptitle('session %s, t in [%.0f, %.0f]s' %\
                (os.path.basename(filename).replace('.nwb',''), *tlim))
    
show_raw(files[0],
    rois = [21, 14, 0, 1, 2, 16, 26])

# %%
from physion.dataviz.imaging import show_singleROI_in_FOV, show_CaImaging_FOV
data = Data(files[0])
show_CaImaging_FOV(data, NL=5,
                   roiIndex=[21, 14, 0, 1, 2, 16, 26],
                   with_ROI_annotation=True)
# %%
rois = list(negROIs[-1][:10])+list(np.arange(20,30))
show_raw(files[-1], rois = rois)

# %%
data = Data(files[-1])
show_CaImaging_FOV(data, NL=5,
                   roiIndex=rois,
                   with_ROI_annotation=True)

# %%
