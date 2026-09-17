# %%
import sys, os
sys.path += ['physion/src']
import physion
from physion.utils import plot_tools as pt
pt.set_style('dark')
import numpy as np

from physion.analysis.read_NWB import Data,\
        scan_folder_for_NWBfiles

from physion.analysis.episodes.build import EpisodeData
# %%
dataset = scan_folder_for_NWBfiles(\
                os.path.join(os.path.expanduser('~'), 
                        'DATA', 'Taddy', 'PN_shGrid1-2026'),
                        for_protocol='plasticity-60')

# %%
dFoF_parameters = dict(\
    roi_to_neuropil_fluo_inclusion_factor=0., # no factor here
    neuropil_correction_factor = 0.5,
    # with_computed_neuropil_fact=True, 
    method_for_F0 = 'sliding_percentile',
    percentile=20., # percent
    sliding_window = 5*60, # seconds
)


# %%

f = dataset['files'][0]
data = Data(f)
data.build_dFoF(**dFoF_parameters)
Ep = EpisodeData(data, prestim_duration=3, quantities=['dFoF'])

# %%
from physion.dataviz.raw import plot as plot_raw, find_default_plot_settings

for f in dataset['files']:

    data = Data(f)
    data.build_dFoF(**dFoF_parameters)
    settings = {'running': {'fig_fraction': 1, 'subsampling': 1, 'color': '#1f77b4'}, 
               'CaImaging': {'fig_fraction': 10, 'subsampling': 1, 'subquantity': 'dF/F',
                                'roiIndices': np.random.choice(np.arange(data.nROIs), np.min([20,data.nROIs]), replace=False),
                                'color': '#2ca02c'}
                }
        # 'FaceMotion': {'fig_fraction': 1, 'subsampling': 1, 'color': 'purple'},
        # 'Pupil': {'fig_fraction': 2, 'subsampling': 1, 'color': '#d62728'},
    _ = plot_raw(data, settings=settings)
# %%

nMax = 6
fig, AX = pt.figure(axes=(nMax, int(data.nROIs/nMax)+1), 
                    wspace=0.4, hspace=0.4, figsize=(1,1))
nTrials = Ep.dFoF.shape[0]
colors = [pt.autumn(r) for r in np.random.uniform(0, 1, data.nROIs)]
for i, ax in enumerate(pt.flatten(AX)):
    if i<data.nROIs:
        for r in range(nTrials):
            ax.plot(Ep.t[::10], Ep.dFoF[r, i, ::10], lw=0.1, 
                    color=colors[i])
        """
        pt.plot(Ep.t, Ep.dFoF[i, :, :].mean(axis=0),
                sy = Ep.dFoF[i,:,:].std(axis=0),
                color=colors[i], ax=ax,lw=0.5)
        """
        pt.shaded_window(ax, xlim=[0,5])
        pt.annotate(ax, 'roi #%i' % (i+1), (1,1), ha='right', color=colors[i])
        pt.draw_bar_scales(ax, Xbar=1, Xbar_label='1s', 
                           Ybar=1, Ybar_label='1$\\Delta$F/F')

    ax.axis('off')

# %%

nTrials = Ep.dFoF.shape[0]

fig, ax = pt.figure(figsize=(2,2))
ax.plot(Ep.t, Ep.dFoF[:,:int(nTrials/2),:].mean(axis=(0,1)),
# ax.plot(Ep.t, Ep.dFoF[:,10:15,:].mean(axis=(0,1)),
        color='tab:blue')
ax.plot(Ep.t, Ep.dFoF[:,int(nTrials/2):,:].mean(axis=(0,1)),
        color='tab:red')

# %%

stat_test_props = dict(interval_pre=[-2.,0],                                   
                       interval_post=[0.,4.],                                   
                       test='ttest',                                            
                       sign='positive')
pval_thresh = 0.01

resps = {'first':[], 'last':[]}

# RESP, sRESP = 'Deconvolved', 'Deconv.'
RESP, sRESP = 'dFoF', '$\Delta$F/F'

for f in dataset['files']:

    data = Data(f)
    data.build_dFoF(**dFoF_parameters)
#     data.build_Deconvolved(Tau=0.8)
    Ep = EpisodeData(data, 
                     prestim_duration=3,
                        quantities=['dFoF',
                                # 'Deconvolved',
                                'running'])
    print(len(Ep.t))

    significant = np.zeros(data.nROIs, dtype=bool)
    for n in range(data.nROIs):
        # summary = Ep.compute_summary_data(\
        summary = Ep.pre_post_statistics(\
                                stat_test_props=stat_test_props,
                                response_args=dict(quantity='dFoF',
                                                   index=n),
                                response_significance_threshold=0.01,
                                verbose=False
                )

        significant[n] = np.sum(summary['significant'])
    
    cond = Ep.running.mean(axis=1)<0.05

    nTrials = Ep.dFoF.shape[0]

    fig, ax = pt.figure(axes=(2,1), figsize=(1.2,1), 
                        wspace=0.7, right=5., top=0.8)
    pt.annotate(fig, f.split('/')[-1], (0.5,1))

    # first half
    Cond = cond & (np.arange(nTrials)<nTrials/2)
    resps['first'].append(\
        getattr(Ep, RESP)[Cond,:,:].mean(axis=0)[significant,:].mean(axis=0))
    ax[0].plot(Ep.t, resps['first'][-1],
            color='tab:blue')

    # second half
    Cond = cond & (np.arange(nTrials)>nTrials/2)
    resps['last'].append(\
        getattr(Ep, RESP)[Cond,:,:].mean(axis=0)[significant,:].mean(axis=0))
    ax[0].plot(Ep.t, resps['last'][-1],
            color='tab:red')
    for i in np.arange(nTrials)[cond]:
        ax[1].plot(Ep.t, 
                   getattr(Ep, RESP)[i,significant,:].mean(axis=0),
                   lw=0.1)
    for x in ax:
        pt.shaded_window(x, xlim=[0,5])
        pt.set_plot(x, 
                    xlabel='time (s)', 
                    ylabel='$\langle$ %s $\\rangle_{ROIs}$' % sRESP)
    pt.annotate(ax[0], '1-%i' % (int(nTrials/2)), (0,1), color='tab:blue')
    pt.annotate(ax[0], '<-trials->', (0.5, 1), ha='center')
    pt.annotate(ax[0], '%i-%i' % (int(nTrials/2)+1, nTrials), (1,1), 
                color='tab:red', ha='right')
    ax[1].set_title('all trials (n=%i)' % nTrials)

    inset = pt.inset(ax[1], (1.3,0.,0.5,1))
    physion.dataviz.imaging.show_CaImaging_FOV(data, ax=inset,
                                               roiIndex=range(data.nROIs))
resps['t'] = Ep.t
# 

# %%
from scipy import stats
fig, ax = pt.figure(right=4)

pre = (resps['t']>-1) & (resps['t']<0)
post = (resps['t']>0) & (resps['t']<1)

for key in ['first', 'last']:
        print(key)
        resps['%s_norm' % key] = np.array([\
                r-np.mean(np.array(r)[pre])\
                        for r in resps[key]])
        resps['%s_norm' % key] = np.array([\
                r/np.max(r[post])\
                        for r in resps['%s_norm' % key]])

pt.plot(resps['t'], np.mean(resps['first_norm'],axis=0),
        sy=stats.sem(resps['first_norm'], axis=0),
        color='tab:blue', ax=ax)
pt.plot(resps['t'], np.mean(resps['last_norm'],axis=0),
        sy=stats.sem(resps['last_norm'], axis=0),
        color='tab:red', ax=ax)

pt.set_plot(ax, xlabel='time (s)', ylabel='%s\n(peak norm.)' % sRESP,
            yticks=[0,1])
pt.annotate(ax, 'first', (1,1), va='top', ha='right', color='tab:blue')
pt.annotate(ax, '\nlast', (1,1), va='top', ha='right', color='tab:red')

inset = pt.inset(ax, [1.7,0.1,0.2,0.8])

window = (resps['t']>0) & (resps['t']<5)
pt.bar([np.mean(100*np.mean(resps['last_norm'][:,window]-\
                            resps['first_norm'][:,window], axis=1))],
       sy=[stats.sem(100*np.mean(resps['last_norm'][:,window]-\
                                 resps['first_norm'][:,window], axis=1))],
       ax=inset)
pt.set_plot(inset, ['left'], 
            title='N=%i' % len(resps['last']),
            ylabel='% change\n $\langle$ last-first $\\rangle$')

# %%
