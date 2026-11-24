# %%
import sys, os
import numpy as np
import matplotlib.pylab as plt
from scipy import stats
sys.path += ['physion/src']
from physion.analysis.read_NWB import Data, scan_folder_for_NWBfiles
from physion.analysis.episodes.build import EpisodeData

from physion.notebook.dataset import markdown_table
from physion.notebook.datafile import single_recording_summary

import physion.utils.plot_tools as pt

import warnings
warnings.filterwarnings("ignore") # disable the UserWarning from pynwb (arrays are not well oriented)

pt.set_style('dark')
notebook = {
    'data-folder':os.path.expanduser(\
        '~/OneDrive - ICM/Lab-Notebook/Data/'),
    'analysis-report':os.path.expanduser(\
        '~/OneDrive - ICM/Lab-Notebook/Projects/Taddy-GluN3/Size-Tuning.md'),
}

# %%
folder = os.path.expanduser('~/DATA/Taddy/SST-WT-GluN1KO-GluN3KO-2023')
# dataset = scan_folder_for_NWBfiles(folder,
#                                    for_protocol='size-tuning')
filenames = [\
    '2023_01_13-15-40-51',
    '2023_01_13-16-56-30',
    '2023_02_16-10-44-38',
    '2023_02_16-13-19-14',
    '2023_02_16-15-10-56',
    '2023_02_16-15-47-31',
    '2023_03_30-11-48-19',
    '2023_03_30-12-46-20',
    '2023_04_20-16-02-15',
    '2023_04_20-16-47-11',
    '2023_04_27-14-27-14',
    '2023_05_05-16-30-30',
    '2023_05_16-15-08-26',
    '2023_06_01-15-02-45',
    '2023_06_01-15-40-17',
    '2023_06_01-16-20-53',
    '2023_06_01-16-56-35',
    '2023_06_01-18-07-23',
    '2023_06_01-18-43-12',
    '2023_06_02-14-39-37',
    '2023_06_02-15-18-26',
    '2023_06_02-16-18-44',
    '2023_06_02-17-30-30',
    '2023_06_07-14-21-49',
    '2023_06_07-14-55-34',
    '2023_06_07-15-29-08',
    '2023_06_07-16-04-01',
    '2023_06_30-14-22-07',
    '2023_06_30-14-59-23',
    '2023_06_30-15-51-25',
    '2023_07_13-14-32-15',
    '2023_07_13-15-04-21',
    '2023_07_13-16-03-32',
    '2023_08_04-12-59-14',
    '2023_08_04-13-41-47',
    '2023_08_04-14-33-52',
    '2023_08_04-15-15-39',
    '2023_08_04-16-00-34',
    '2023_08_30-12-20-15',
    '2023_08_30-13-33-48',
    '2023_08_30-14-40-39',
    '2023_08_30-15-23-54',
    '2023_08_30-16-08-27',
    '2023_08_30-17-08-22',
    '2023_10_06-13-25-57',
    '2023_10_06-14-03-17',
    '2023_10_06-15-03-44',
    '2023_10_06-16-21-50',
    '2023_10_06-17-00-22',
    '2023_11_03-14-05-41',
    '2023_11_03-15-02-52',
    '2023_11_03-15-42-41',
    '2023_11_03-16-58-21',
    '2023_11_03-17-42-12',
    '2023_11_03-18-31-28',
    ]
dataset = scan_folder_for_NWBfiles(folder, 
                                   for_protocol='size-tuning', 
                                   from_filenames=filenames)
# %%
markdown_table(dataset,
               keys=['files', 'subjects', 'protocol'],
                append_to=notebook['analysis-report'])

# %%

def build_quantity(data, quantity,
                   roi_to_neuropil_fluo_inclusion_factor=1.15,
                   neuropil_correction_factor=0.7,
                   method_for_F0='sliding_percentile',
                   percentile=5.,
                   sliding_window=300,
                   verbose=False):
    """
    builds "quantity" in data, one of:
        'correctedFluo' = rawFluo - neuropil_correction_factor x neuropil
        'dFoF'          = (correctedFluo-F0)/F0
        'rawFluo', 'neuropil'
    the ROIs are restricted to the ones with fluo > inclusion_factor x neuropil
        (for dFoF: also the ones with a positive F0 baseline)
    """

    data.build_rawFluo(verbose=verbose)
    data.build_neuropil(verbose=verbose)

    if 'dFoF' in quantity:
        data.build_dFoF(roi_to_neuropil_fluo_inclusion_factor=\
                                roi_to_neuropil_fluo_inclusion_factor,
                        method_for_F0=method_for_F0,
                        percentile=percentile,
                        sliding_window=sliding_window,
                        neuropil_correction_factor=neuropil_correction_factor,
                        verbose=verbose)
        if 'Deconvolved' in quantity:
            data.build_Deconvolved(quantity='dFoF')

    elif quantity=='Deconvolved':
        data.build_correctedFluo(neuropil_correction_factor=\
                                        neuropil_correction_factor,
                                    verbose=verbose)
        data.build_Deconvolved(quantity='correctedFluo')

    elif quantity in ['correctedFluo', 'rawFluo', 'neuropil']:
        if quantity=='correctedFluo':
            data.build_correctedFluo(neuropil_correction_factor=\
                                            neuropil_correction_factor,
                                     verbose=verbose)
        data.set_valid_roiIndices(roi_to_neuropil_fluo_inclusion_factor=\
                                        roi_to_neuropil_fluo_inclusion_factor,
                                  verbose=verbose)
    else:
        raise ValueError('quantity "%s" not recognized !!' % quantity)

# %%
def plot_roi_responses(data, index,
                       quantity='Deconvolved',
                       angle=None,
                       prestim_duration=2,
                       EPISODES=None,
                       color=None):
    """
    responses of a single ROI to the two size-tuning protocols:
        left:  3x3 insets, mean response at each (x-center, y-center)
                    of 'size-tuning-protocol-loc' (top row = highest y-center)
        right: mean response for increasing radius
                    of 'size-tuning-protocol-dep'

    angle=None -> average over all angles, otherwise restricted to that angle
    EPISODES: optional dict {'loc':EpisodeData, 'dep':EpisodeData}, filled at
              first call, pass it back to avoid rebuilding when looping over ROIs
    """
    if EPISODES is None:
        EPISODES = {}
    for key in ['loc', 'dep']:
        if key not in EPISODES:
            protocol_id = np.flatnonzero([('size-tuning-protocol-%s' % key) in p\
                                                for p in data.protocols])[0]
            EPISODES[key] = EpisodeData(data,
                                        protocol_id=protocol_id,
                                        quantities=[quantity],
                                        prestim_duration=prestim_duration,
                                        verbose=False)
    loc, dep = EPISODES['loc'], EPISODES['dep']

    if color is None:
        color = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]

    def mean_response(episodes, keys, values, ax):
        if (angle is not None) and ('angle' in episodes.varied_parameters):
            keys, values = keys+['angle'], values+[angle]
        cond = episodes.find_episode_cond(key=keys, value=values)
        resp = episodes.get_response2D(quantity=quantity,
                                       episode_cond=cond,
                                       index=int(index))
        m, s = resp.mean(axis=0), stats.sem(resp, axis=0)
        stim_dur = episodes.t[-1]+episodes.t[0] # t spans [-pre, dur+pre]
        ax.axvspan(0, stim_dur, color='grey', alpha=0.25, lw=0)
        ax.fill_between(episodes.t, m-s, m+s, color=color, alpha=0.3, lw=0)
        ax.plot(episodes.t, m, color=color, lw=1)
        ax.axis('off')

    xs, ys = loc.varied_parameters['x-center'], loc.varied_parameters['y-center']
    radii = dep.varied_parameters['radius']

    fig = plt.figure(figsize=(1.3+0.8*len(radii), 1.3))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.3, 0.8*len(radii)], wspace=0.15,
                          left=0.08, right=0.98, bottom=0.05, top=0.8)
    gsLoc = gs[0].subgridspec(len(ys), len(xs), wspace=0.05, hspace=0.05)
    gsDep = gs[1].subgridspec(1, len(radii), wspace=0.1)

    # --- 3x3 centering insets
    AX_loc = []
    for i, y in enumerate(ys[::-1]):
        for j, x in enumerate(xs):
            ax = fig.add_subplot(gsLoc[i, j])
            mean_response(loc, ['x-center', 'y-center'], [x, y], ax)
            AX_loc.append(ax)
    AX_loc[1].set_title('position', fontsize=7)
    AX_loc[0].annotate('roi #%i  ' % (index+1), (0, 0.5), ha='right', va='center',
                       rotation=90, xycoords='axes fraction', fontsize=7)

    # --- size dependency
    AX_dep = []
    for k, r in enumerate(radii):
        ax = fig.add_subplot(gsDep[0, k])
        mean_response(dep, ['radius'], [r], ax)
        ax.set_title(r'r=%i$^o$' % r, fontsize=7)
        AX_dep.append(ax)

    pt.set_common_ylims(AX_loc+AX_dep)
    pt.draw_bar_scales(AX_dep[0], Xbar=1, Xbar_label='1s',
                       Ybar=0, Ybar_label_format='%.2f', fontsize=6,
                       loc='top-left', color=color)
    return fig, EPISODES

# %%
data = Data(dataset['files'][-1])
build_quantity(data, 'Deconvolved')
fig, EPISODES = plot_roi_responses(data, 10)

# %%
ROI_SECTION = '## Single ROI responses'

def add_roi_examples_to_summary(filename, notebook_folder,
                                N=20,
                                quantity='Deconvolved',
                                quantity_args={},
                                seed=1,
                                verbose=True):
    """
    appends to the notebook page "filename.md" (written by single_recording_summary)
        N random ROIs plotted with plot_roi_responses
        (figures in "notebook_folder/figs/filename-roi-XX.svg")
    a previous "Single ROI responses" section is replaced (so re-running is safe)
    """
    fn = os.path.basename(filename).replace('.nwb', '')
    md = os.path.join(notebook_folder, fn+'.md')
    os.makedirs(os.path.join(notebook_folder, 'figs'), exist_ok=True)

    data = Data(filename, verbose=False)
    build_quantity(data, quantity, **quantity_args)

    np.random.seed(seed)
    rois = np.sort(np.random.choice(np.arange(data.nROIs),
                                    min([N, data.nROIs]), replace=False))

    text = '\n%s \n\n' % ROI_SECTION
    text += '%i random ROIs (/%i), "%s" \n' % (len(rois), data.nROIs, quantity)
    text += '- left: 3x3 positions of "size-tuning-protocol-loc" \n'
    text += '- right: increasing radius of "size-tuning-protocol-dep" \n\n'

    EPISODES = None
    for roi in rois:
        fig, EPISODES = plot_roi_responses(data, roi,
                                           quantity=quantity,
                                           EPISODES=EPISODES)
        svg = '%s-roi-%i.svg' % (fn, roi+1)
        fig.savefig(os.path.join(notebook_folder, 'figs', svg))
        plt.close(fig)
        text += '![](figs/%s)    \n' % svg
    data.close()

    # replace any previous ROI section (always at the end of the page)
    previous = open(md).read() if os.path.isfile(md) else ''
    previous = previous.split('\n'+ROI_SECTION)[0]
    with open(md, 'w') as f:
        f.write(previous+text)
    if verbose:
        print(' -> %i ROI plots added to %s' % (len(rois), md))

# %%
REDO_ALL_SINGLE_RECORDINGS_FIGS = False # turn True
ADD_ROI_EXAMPLES = True # turn True
for f in dataset['files']:
    if REDO_ALL_SINGLE_RECORDINGS_FIGS:
        single_recording_summary(f,
                notebook_folder=notebook['data-folder'])
    if ADD_ROI_EXAMPLES:
        try:
            add_roi_examples_to_summary(f, notebook['data-folder'], N=20)
        except Exception as be:
            print(' [!!] ROI examples failed for "%s" :' % f, be)

# %%

GENOTYPES = ['WT', 'GluN1', 'GluN3']
COLORS = {'WT':'k', 'GluN1':'tab:blue', 'GluN3':'g'}

def init_summary(dataset):

    SUMMARY = {key:{'FILES':[], 'subjects':[]} for key in GENOTYPES}

    for i, protocols in enumerate(dataset['protocols']):

        # sort the sessions according to the mouse genotype
        if ('NR1' in dataset['subjects'][i]) or ('GluN1' in dataset['subjects'][i]):
            key = 'GluN1'
        elif ('NR3' in dataset['subjects'][i]) or ('GluN3' in dataset['subjects'][i]):
            key = 'GluN3'
        else:
            key = 'WT'
        SUMMARY[key]['FILES'].append(dataset['files'][i])
        SUMMARY[key]['subjects'].append(dataset['subjects'][i])

    return SUMMARY


# %% [markdown]
# ## Analysis

# %%
# (re-implementation of physion.analysis.protocols.size_tuning,
#        with the new EpisodeData statistics: "pre_post_statistics")

stat_test_props = dict(interval_pre=[-1,0],
                       interval_post=[0,1],
                       test='ttest',
                       sign='positive')

def protocol_id_containing(data, name):
    return np.flatnonzero([(name in p) for p in data.protocols])[0]

def center_and_compute_size_tuning(data,
                                   imaging_quantity='Deconvolved',
                                   prestim_duration=2,
                                   response_significance_threshold=0.05,
                                   stat_test_props=stat_test_props,
                                   verbose=False):
    """
    1) centering protocol: ROIs with a significant response at the center
            and whose maximum response is at the center (+ their prefered angle)
    2) size-tuning protocol: responses of those ROIs at their prefered angle

    returns radii, size_resps, centered_rois, angles
    """

    # ## --- EPISODES -- CENTERING
    episodes = EpisodeData(data,
                           protocol_id=protocol_id_containing(data, 'size-tuning-protocol-loc'),
                           quantities=[imaging_quantity],
                           prestim_duration=prestim_duration,
                           verbose=verbose)
    # summary of shape (nROIs, nConditions)
    resp = episodes.pre_post_statistics(response_args=dict(quantity=imaging_quantity),
                                        stat_test_props=stat_test_props,
                                        response_significance_threshold=\
                                                response_significance_threshold,
                                        loop_over_cells=True,
                                        verbose=False)

    center_cond = (resp['x-center']==0) & (resp['y-center']==0)
    CENTERED_ROIS, ANGLES = [], []
    for roi in range(resp['value'].shape[0]):
        if (np.sum(resp['significant'][roi][center_cond])>0) and\
                (np.max(resp['value'][roi]) in resp['value'][roi][center_cond]):
            # if significant and max responses
            CENTERED_ROIS.append(roi) # we add the ROI
            iangle = np.argmax(resp['value'][roi][center_cond])
            ANGLES.append(resp['angle'][center_cond][iangle]) # and we store the best angle

    # ## --- EPISODES -- SIZE VARIATIONS
    episodes = EpisodeData(data,
                           protocol_id=protocol_id_containing(data, 'size-tuning-protocol-dep'),
                           quantities=[imaging_quantity],
                           prestim_duration=prestim_duration,
                           verbose=verbose)

    radii, SIZE_RESPS = [], []
    if len(CENTERED_ROIS)>0:
        resp = episodes.pre_post_statistics(response_args=dict(quantity=imaging_quantity),
                                            stat_test_props=stat_test_props,
                                            response_significance_threshold=\
                                                    response_significance_threshold,
                                            loop_over_cells=True,
                                            verbose=False)
        for roi, angle in zip(CENTERED_ROIS, ANGLES):
            angle_cond = (resp['angle']==angle)
            isort = np.argsort(resp['radius'][angle_cond])
            SIZE_RESPS.append(np.concatenate([[0], resp['value'][roi][angle_cond][isort]]))
        radii = np.concatenate([[0], np.sort(resp['radius'][angle_cond])])

    return radii, SIZE_RESPS, CENTERED_ROIS, ANGLES



def run_dataset_analysis(dataset,
                         quantity='Deconvolved',
                         roi_to_neuropil_fluo_inclusion_factor=1.15,
                         neuropil_correction_factor = 0.7,
                         method_for_F0 = 'sliding_percentile',
                         percentile=5., # percent
                         sliding_window = 300, # seconds
                         Nmax=999, # max datafiles (for debugging)
                         verbose=True):

    SUMMARY = init_summary(dataset)

    SUMMARY['quantity'] = quantity
    SUMMARY['quantity_args'] = dict(roi_to_neuropil_fluo_inclusion_factor=\
                                        roi_to_neuropil_fluo_inclusion_factor,
                                    method_for_F0=method_for_F0,
                                    percentile=percentile,
                                    sliding_window=sliding_window,
                                    neuropil_correction_factor=neuropil_correction_factor)

    for key in GENOTYPES:

        for k in ['RESPONSES', 'CENTERED_ROIS', 'PREF_ANGLES']:
            SUMMARY[key][k] = []

        for f in SUMMARY[key]['FILES'][:Nmax]:

            print('analyzing "%s" [...] ' % f)
            data = Data(f, verbose=False)

            build_quantity(data, quantity,
                           **SUMMARY['quantity_args'])

            radii, size_resps, rois, pref_angles = \
                    center_and_compute_size_tuning(data,
                                                   imaging_quantity=quantity,
                                                   verbose=False)
            if len(size_resps)>0:
                for k, q in zip(['RESPONSES', 'CENTERED_ROIS', 'PREF_ANGLES'],
                                [size_resps, rois, pref_angles]):
                    SUMMARY[key][k].append(q)

            if len(radii)>0:
                SUMMARY['radii'] = radii

            data.close()

    return SUMMARY

# %%
os.makedirs('data', exist_ok=True)

quantity='Deconvolved'
SUMMARY = run_dataset_analysis(dataset, 
                               quantity=quantity,
                               verbose=False,
                               Nmax=2)
np.save('data/%s-summary.npy' % quantity, SUMMARY)

# %% [markdown]
# ## Quantification & Data visualization

# %%
from scipy.special import erf
from scipy.optimize import minimize

QUANTITY_LABELS = {'dFoF':r'$\Delta$F/F',
                   'correctedFluo':'corr. fluo (a.u.)',
                   'correctedFluo':'corr. fluo (a.u.)',
                   'rawFluo':'raw fluo (a.u.)',
                   'neuropil':'neuropil (a.u.)'}

def func(S, X):
    """ fitting function """
    return X[0]*(erf(S/X[1])-X[3]*erf(S/X[2]))

def angle_lin_to_true_angle(angle):
    """
    see:
    https://github.com/yzerlaut/physion/blob/main/notebooks/Visual-Stim-Design.ipynb
    """
    return 180./np.pi*np.arctan(angle/180.*np.pi)

def suppression_index(resp1, resp2):
    resp1 = np.clip(resp1, 1e-2, np.inf)
    return np.clip((resp1-resp2)/resp1, 0, 1)

def plot_summary(SUMMARY,
                 average_by='sessions',
                 xscale='lin', ms=2):

    # only the genotypes with data
    keys = [key for key in GENOTYPES if len(SUMMARY[key]['RESPONSES'])>0]

    fig, AX = plt.subplots(1, len(keys), figsize=(1.75*len(keys),1.), squeeze=False)
    AX = AX[0]
    AX[0].annotate('average\nover\n%s' % average_by,
                   (-0.8, 0.5), va='center', ha='center', xycoords='axes fraction')
    plt.subplots_adjust(wspace=0.7)

    inset = pt.inset(AX[-1], [1.6, .2, .4, .8])

    stim_size = 2*angle_lin_to_true_angle(SUMMARY['radii']) # radius to diameter, and linear-approx correction
    SIs = []

    for i, key in enumerate(keys):

        color = COLORS[key]

        if average_by=='sessions':
            resp = np.array([np.mean(np.clip(r, 0, np.inf), axis=0) for r in SUMMARY[key]['RESPONSES']])
        else:
            resp = np.concatenate([np.clip(r, 0, np.inf) for r in SUMMARY[key]['RESPONSES']])

        SIs.append([suppression_index(np.mean(r[2:5]), np.mean(r[-3:])) for r in resp])

        # data
        pt.scatter(stim_size, np.mean(resp, axis=0),
                   sy=stats.sem(resp, axis=0),
                   ax=AX[i], color=color, ms=ms)

        # fit
        def to_minimize(x0):
            return np.sum((resp.mean(axis=0)-\
                           func(stim_size, x0))**2)
        res = minimize(to_minimize,
                       [2, 20, 40, 0])
        x = np.linspace(0, stim_size[-1], 100)
        AX[i].plot(x, func(x, res.x), lw=2, alpha=.5, color=color)

        AX[i].set_title(key, color=color)
        if average_by=='sessions':
            inset.annotate(i*'\n'+'\nN=%i %s (%i ROIs, %i mice)' % (len(resp),
                                                average_by, np.sum([len(r) for r in SUMMARY[key]['RESPONSES']]),
                                                len(np.unique(SUMMARY[key]['subjects']))),
                           (0,0), fontsize=7,
                           va='top',color=color, xycoords='axes fraction')
        else:
            inset.annotate(i*'\n'+'\nn=%i %s (%i sessions, %i mice)' % (len(resp),
                                                average_by, len(SUMMARY[key]['RESPONSES']),
                                                                len(np.unique(SUMMARY[key]['subjects']))),
                           (0,0), fontsize=7,
                           va='top',color=color, xycoords='axes fraction')

    # suppression index
    for i, key in enumerate(keys):
        pt.violin(SIs[i], x=i, ax=inset, color=COLORS[key])
    # stat. test of each genotype vs the first one (WT)
    for i in range(1, len(keys)):
        inset.plot([0,i], (1+0.1*i)*np.ones(2), '-', color='grey', lw=0.5)
        inset.annotate('p=%.1e' % stats.mannwhitneyu(SIs[0], SIs[i]).pvalue,
                       (i/2., 1.03+0.1*i), ha='center', fontsize=6)

    ylabel = r'$\delta$ %s' % QUANTITY_LABELS.get(SUMMARY['quantity'], SUMMARY['quantity'])
    for ax in AX:
        if xscale=='log':
            pt.set_plot(ax, xlabel=r'stim. size ($^o$)',
                        xscale='log', #xticks=[10,100], xticks_labels=['10', '100'], xlim=[9,109],
                        ylabel=ylabel)
        else:
            pt.set_plot(ax, xlabel=r'stim. size ($^o$)',
                        xticks=[0, 40, 80, 120], xticks_labels=['0', '40', '80', 'FF'],
                        ylabel=ylabel)
    pt.set_common_ylims(AX)
    pt.set_plot(inset, xticks=[], ylabel='suppr. index', yticks=[0, 0.5, 1],
                ylim=[0, 1.05+0.1*len(keys)])
    return fig

SUMMARY = np.load('data/correctedFluo-summary.npy', 
                  allow_pickle=True).item()
fig = plot_summary(SUMMARY, average_by='ROIs')
fig = plot_summary(SUMMARY, average_by='sessions')

# %% [markdown]
# ## Varying the preprocessing parameters

# %%
for quantity in ['rawFluo', 'neuropil', 'correctedFluo', 'dFoF']:
    SUMMARY = run_dataset_analysis(dataset, quantity=quantity, verbose=False)
    np.save('data/%s-summary.npy' % quantity, SUMMARY)

for neuropil_correction_factor in [0.6, 0.7, 0.8, 0.9]:
    SUMMARY = run_dataset_analysis(dataset, quantity='correctedFluo',
                                   neuropil_correction_factor=neuropil_correction_factor,
                                   verbose=False)
    np.save('data/factor-neuropil-%.1f-summary.npy' % neuropil_correction_factor, SUMMARY)

for roi_to_neuropil_fluo_inclusion_factor in [1.05, 1.1, 1.15, 1.2, 1.25, 1.3]:
    SUMMARY = run_dataset_analysis(dataset,
                                   quantity='correctedFluo',
                                   roi_to_neuropil_fluo_inclusion_factor=roi_to_neuropil_fluo_inclusion_factor,
                                   verbose=False)
    np.save('data/inclusion-factor-neuropil-%.2f-summary.npy' % roi_to_neuropil_fluo_inclusion_factor, SUMMARY)

# %%
for quantity in ['rawFluo', 'neuropil', 'correctedFluo', 'dFoF']:
    SUMMARY = np.load('data/%s-summary.npy' % quantity, allow_pickle=True).item()
    fig = plot_summary(SUMMARY, average_by='ROIs')

# %%
for neuropil_correction_factor in [0.6, 0.7, 0.8, 0.9]:
    SUMMARY = np.load('data/factor-neuropil-%.1f-summary.npy' % neuropil_correction_factor,
                      allow_pickle=True).item()
    fig = plot_summary(SUMMARY, average_by='ROIs')
    plt.annotate('Neuropil-factor for substraction: %.1f\n\n' % neuropil_correction_factor,
                 (1,1), xycoords='axes fraction')

# %%
for roi_to_neuropil_fluo_inclusion_factor in [1.05, 1.1, 1.15, 1.2, 1.25, 1.3]:
    SUMMARY = np.load('data/inclusion-factor-neuropil-%.2f-summary.npy' % roi_to_neuropil_fluo_inclusion_factor,
                      allow_pickle=True).item()
    fig = plot_summary(SUMMARY, average_by='ROIs')
    plt.annotate('roiFluo/Neuropil inclusion-factor: %.2f\n' % roi_to_neuropil_fluo_inclusion_factor,
                 (1,1), xycoords='axes fraction')

# %% [markdown]
# # Visualizing some evoked response in single ROI

# %%
data = Data(dataset['files'][0])
print(data.protocols)
data.get_protocol_id('size-tuning-protocol-loc')

# %%
from physion.dataviz.episodes.trial_average import plot as plot_trial_average

def load_with_visual_stim(filename):
    """ Data with the visual stim if it can be rebuilt (otherwise data.visual_stim=None) """
    data = Data(filename)
    try:
        data.build_visual_stim()
    except Exception as be:
        print(' [!!] visual stim not rebuilt (no screen inset) :', be)
        data.visual_stim = None
    return data

def cell_tuning_example_fig(filename,
                            protocol='size-tuning-protocol-loc',
                            quantity='correctedFluo',
                            quantity_args={},
                            condition_key='angle',
                            stat_test_props = dict(interval_pre=[-1,0],
                                                   interval_post=[1,2],
                                                   test='ttest',
                                                   sign='positive'),
                            response_significance_threshold = 0.01,
                            Ybar=1., Ybar_label='1a.u.',
                            Nsamples = 10, # how many cells we show
                            seed=10):

    np.random.seed(seed)

    data = load_with_visual_stim(filename)
    build_quantity(data, quantity, **quantity_args)

    EPISODES = EpisodeData(data,
                           quantities=[quantity],
                           protocol_id=protocol_id_containing(data, protocol),
                           verbose=True)

    fig, AX = plt.subplots(Nsamples, len(EPISODES.varied_parameters[condition_key]),
                          figsize=(7,7))
    plt.subplots_adjust(right=0.75, left=0.1, top=0.97, bottom=0.05, wspace=0.1, hspace=0.8)

    for Ax in AX:
        for ax in Ax:
            ax.axis('off')

    for i, r in enumerate(np.random.choice(np.arange(data.nROIs),
                                           min([Nsamples, data.nROIs]), replace=False)):

        # SHOW trial-average
        plot_trial_average(EPISODES,
                           column_key=condition_key,
                           quantity=quantity,
                           Ybar=Ybar, Ybar_label=Ybar_label,
                           Xbar=1., Xbar_label='1s',
                           index=r,
                           with_stat_test=True,
                           stat_test_props=stat_test_props,
                           with_screen_inset=(data.visual_stim is not None),
                           AX=[AX[i]], no_set=False)
        AX[i][0].annotate('roi #%i  ' % (r+1), (0,0), ha='right', xycoords='axes fraction')

        # SHOW summary dependence on the condition key
        inset = pt.inset(AX[i][-1], (2.2, 0.2, 1.2, 0.8))

        values, y, sy = [], [], []
        responsive = False

        for value in EPISODES.varied_parameters[condition_key]:

            st = EPISODES.stat_test_for_evoked_responses(episode_cond=\
                                            EPISODES.find_episode_cond(key=condition_key,
                                                                       value=value),
                                                         response_args=dict(quantity=quantity, index=r),
                                                         verbose=False,
                                                         **stat_test_props)

            values.append(value)
            y.append(np.mean(st.y-st.x))    # means "post-pre"
            sy.append(np.std(st.y-st.x))    # std "post-pre"

            if st.significant(threshold=response_significance_threshold):
                responsive = True

        pt.plot(values, np.array(y), sy=np.array(sy), ax=inset)
        inset.plot(values, 0*np.array(values), 'k:', lw=0.5)
        inset.set_ylabel(r'$\delta$ %s     ' % QUANTITY_LABELS.get(quantity, quantity), fontsize=7)
        inset.set_xticks(values)
        inset.set_xticklabels(['%i'%a if (k%2==0) else '' for k, a in enumerate(values)], fontsize=7)
        if i==(Nsamples-1):
            inset.set_xlabel('%s' % condition_key, fontsize=7)

        inset.annotate(('responsive' if responsive else 'unresponsive'), (1, 1), ha='right',
                        weight='bold', fontsize=6, color=(plt.cm.tab10(2) if responsive else plt.cm.tab10(3)),
                        xycoords='axes fraction')

    return fig

SUMMARY = init_summary(dataset)
fig = cell_tuning_example_fig(SUMMARY['GluN1']['FILES'][0])

# %%
fig = cell_tuning_example_fig(SUMMARY['GluN3']['FILES'][0])

# %% [markdown]
# # Visualizing some raw population data

# %%
from physion.dataviz.raw import plot as plot_raw
from physion.dataviz.imaging import show_CaImaging_FOV

data = load_with_visual_stim(dataset['files'][0])
build_quantity(data, 'correctedFluo')

def raw_settings(data, subsampling=1):
    settings = {}
    for key, color, fraction in zip(['running', 'facemotion', 'pupil'],
                                    ['#1f77b4', 'purple', '#d62728'],
                                    [1, 1, 2]):
        if getattr(data, 'has_%s' % key)():
            getattr(data, 'build_%s' % key)()
            settings[key] = {'fig_fraction': fraction, 'subsampling': subsampling, 'color': color}
    settings['CaImaging'] = {'fig_fraction': 4,
                             'subsampling': 1,
                             'subquantity': 'correctedFluo',
                             'color': '#2ca02c',
                             'roiIndices': np.random.choice(np.arange(data.nROIs), 5, replace=False)}
    settings['CaImagingRaster'] = {'fig_fraction': 3,
                                   'subsampling': 1,
                                   'raster': data.correctedFluo,
                                   'roiIndices': np.arange(data.nROIs),
                                   'normalization': 'per-line',
                                   'subquantity': 'correctedFluo'}
    return settings

settings = raw_settings(data)
settings['visual_stim'] = {'fig_fraction': 0.5, 'color': 'black', 'with_screen_inset':True}
tlim = [984,1100]
plot_raw(data, tlim=tlim, settings=settings)

# %%
settings = raw_settings(data, subsampling=2)
tlim = [900, 1300]
plot_raw(data, tlim=tlim, settings=settings)

# %%
show_CaImaging_FOV(data, key='max_proj', NL=3, roiIndex=list(data.valid_roiIndices))

# %%
show_CaImaging_FOV(data, key='max_proj', NL=3)

# %%
folder = os.path.expanduser('~/DATA/Taddy/SST-WT-GluN1KO-GluN3KO-2023')
dataset = scan_folder_for_NWBfiles(folder)

notebook = {
    'data-folder':os.path.expanduser(\
        '~/OneDrive - ICM/Lab-Notebook/Data/'),
    'analysis-report':os.path.expanduser(\
        '~/OneDrive - ICM/Lab-Notebook/Projects/Taddy-GluN3/Size-Tuning.md'),
}
# %%
