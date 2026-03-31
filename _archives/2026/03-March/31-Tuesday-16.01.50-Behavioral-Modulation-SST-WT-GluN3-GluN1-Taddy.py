# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Behavioral modulation of visually Evoked Activity

# %%
# general python modules
import sys, os, pprint, pandas
import numpy as np
import matplotlib.pylab as plt
from scipy import stats

sys.path.append(os.path.join(os.path.expanduser('~'), 'work', 'physion', 'src'))

from physion.analysis.read_NWB import Data, scan_folder_for_NWBfiles
from physion.analysis.process_NWB import EpisodeData
import physion.utils.plot_tools as pt

iFig = 0
Fig_Folder = os.path.join('/Volumes', 'T7 Touch', 'FIGURES_SSTs')

# %%
DATASET = {\
    'WT':scan_folder_for_NWBfiles(os.path.join(os.path.expanduser('~'), 'DATA', 'Taddy', 'SST-WT', 'Orient-Tuning', 'NWBs')),
    'GluN1KO':scan_folder_for_NWBfiles(os.path.join(os.path.expanduser('~'), 'DATA', 'Taddy', 'SST-cond-GluN1KO', 'Orient-Tuning', 'NWBs')),
    'GluN3KO':scan_folder_for_NWBfiles(os.path.join(os.path.expanduser('~'), 'DATA', 'Taddy', 'SST-GluN3KO', 'Orient-Tuning', 'NWBs')),
}

# %% [markdown]
# ## Loading and Analyzing Sessions

# %%
Responses = {}

speed_threshold = 0.1

cases, colors = DATASET.keys(), ['tab:orange', 'tab:purple', 'tab:green']

for i, case in enumerate(cases):
    
    Responses['%s_run' % case] = []
    Responses['%s_rest' % case] = []
    
    for n, f in enumerate(DATASET[case]['files']):
        
        print(' - analyzing file # %i: %s  [...] ' % (n+1, f))
        data = Data(f, verbose=False)
        data.build_dFoF(method_for_F0='sliding_percentile', neuropil_correction_factor=0.7, percentile=10., verbose=False)
    
        Episodes = EpisodeData(data, 
                            quantities=['dFoF', 'running_speed'],
                            protocol_name=[p for p in data.protocols if 'ff-gratings' in p][0],
                            verbose=False, prestim_duration=3,
                            dt_sampling=10)
    
        # Run vs Rest :
        withinEpisode_cond = (Episodes.t>0) & (Episodes.t<Episodes.time_duration[0])
        Ep_run_speed = Episodes.running_speed[:,withinEpisode_cond].mean(axis=1)
        run = Ep_run_speed>speed_threshold
        
        Responses['%s_run' % case].append(np.mean(Episodes.dFoF[run,:,:], axis=0))
        Responses['%s_rest' % case].append(np.mean(Episodes.dFoF[~run,:,:], axis=0))
        
    Responses['t'] = Episodes.t

# %% [markdown]
# ## Analysis Per Session

# %%
from scipy.optimize import minimize

fig, AX = pt.figure(axes=(3,2))
inset = pt.inset(AX[-1][-1], [1.9, 1., 0.6, 1.])

baselineCond = (Episodes.t>-0.1) & (Episodes.t<0)

gains = {}
for i, case in enumerate(cases):

    for cond, color in zip(['run', 'rest'], ['tab:red', 'tab:blue']):

        # means of each session:
        means = [np.mean(r, axis=0) for r in Responses['%s_%s' % (case, cond)]]
        
        pt.plot(Responses['t'], np.mean(means, axis=0), 
                sy = stats.sem(means, axis=0), color=color, no_set=True, ax=AX[0][i])
    
        Responses['baselineSubstr_%s_%s' % (case, cond)] = [r-r[baselineCond].min() for r in means]
        
        pt.plot(Responses['t'], np.mean(Responses['baselineSubstr_%s_%s' % (case, cond)], axis=0), 
                sy = stats.sem(Responses['baselineSubstr_%s_%s' % (case, cond)], axis=0), color=color, no_set=True, ax=AX[1][i])
    
    pt.set_plot(AX[0][i], ylabel='$\delta$ $\Delta$F/F', xlim=[-1, Responses['t'][-1]])
    AX[0][i].set_title(case+'\nN=%i sessions' % len(Responses['%s_%s' % (case, cond)]), color=colors[i])

    t_cond = Responses['t']>(-0.1)
    
    pt.set_plot(AX[1][i], ylabel='B.S. $\delta$ $\Delta$F/F', 
                xlabel='time from stim. (s)' , xlim=[-.1, Responses['t'][-1]])
    
    gains[case] = []
    
    for j in range(len(Responses['%s_run' % case])):
        
        def to_minimize(X):
            return np.sum((X[0]*Responses['baselineSubstr_%s_rest' % case][j][t_cond]-
                           Responses['baselineSubstr_%s_run' % case][j][t_cond])**2)
            
        res = minimize(to_minimize, [1.05])
        gains[case].append(res.x[0])
        
    AX[1][i].plot(np.array(Responses['t'])[t_cond], 
               np.mean(gains[case])*np.mean(Responses['baselineSubstr_%s_rest' % case], axis=0)[t_cond], 'k:', lw=0.5)

    print(case, 'gain = %.2f $\pm$ %.2f' % (np.mean(gains[case]), stats.sem(gains[case])))
    pt.bar([np.mean(gains[case])], x=[i], sy=[stats.sem(gains[case])], color=colors[i], ax=inset)

for i, (case1, case2) in enumerate([['WT', 'GluN1KO'], ['GluN1KO', 'GluN3KO'], ['WT', 'GluN3KO']]):
    pval = stats.mannwhitneyu(gains[case1], gains[case2]).pvalue
    
    pt.annotate(inset, '%s vs %s: %s, p=%.1e ' % (case1, case2, pt.from_pval_to_star(pval), pval) + i*'\n',
                #'%s vs %s, %s, p=%.1e ' (case1, case2, pt.from_pval_to_star(pval), pval) + i*'\n',
               (0.5, 1.09), fontsize=6, ha='center')

pt.set_plot(inset, ['left'], ylabel='gain')

iFig +=1
fig.savefig(os.path.join(Fig_Folder, 'BM-%i.svg' % iFig))

# %% [markdown]
# ## Analysis Per ROIs

# %%
from scipy.optimize import minimize

fig, AX = pt.figure(axes=(3,2))
inset = pt.inset(AX[-1][-1], [1.9, 1., 0.6, 1.])

# wider baseline to average more:
baselineCond = (Episodes.t>-0.2) & (Episodes.t<0)

gains = {}
for i, case in enumerate(cases):

    for cond, color in zip(['run', 'rest'], ['tab:red', 'tab:blue']):

        # means of each ROI :
        means = np.concatenate(Responses['%s_%s' % (case, cond)])
        
        pt.plot(Responses['t'], np.mean(means, axis=0), 
                sy = stats.sem(means, axis=0), color=color, no_set=True, ax=AX[0][i])
    
        Responses['baselineSubstr_%s_%s' % (case, cond)] = [r-r[baselineCond].min() for r in means]
        
        pt.plot(Responses['t'], np.mean(Responses['baselineSubstr_%s_%s' % (case, cond)], axis=0), 
                sy = stats.sem(Responses['baselineSubstr_%s_%s' % (case, cond)], axis=0), color=color, no_set=True, ax=AX[1][i])
    
    pt.set_plot(AX[0][i], ylabel='$\delta$ $\Delta$F/F', xlim=[-1, Responses['t'][-1]])
    AX[0][i].set_title(case+'\nn=%i ROIs' % len(means), color=colors[i])

    t_cond = Responses['t']>(-0.1)
    
    pt.set_plot(AX[1][i], ylabel='B.S. $\delta$ $\Delta$F/F', 
                xlabel='time from stim. (s)' , xlim=[-.1, Responses['t'][-1]])
    
    gains[case] = []
    
    for j in range(len(means)):
        
        def to_minimize(X):
            return np.sum((X[0]*Responses['baselineSubstr_%s_rest' % case][j][t_cond]-
                           Responses['baselineSubstr_%s_run' % case][j][t_cond])**2)
            
        res = minimize(to_minimize, [1.05])
        gains[case].append(res.x[0])
        
    AX[1][i].plot(np.array(Responses['t'])[t_cond], 
               np.mean(gains[case])*np.mean(Responses['baselineSubstr_%s_rest' % case], axis=0)[t_cond], 'k:', lw=0.5)

    print(case, 'gain = %.2f $\pm$ %.2f' % (np.mean(gains[case]), stats.sem(gains[case])))
    pt.bar([np.mean(gains[case])], x=[i], sy=[stats.sem(gains[case])], color=colors[i], ax=inset)

for i, (case1, case2) in enumerate([['WT', 'GluN1KO'], ['GluN1KO', 'GluN3KO'], ['WT', 'GluN3KO']]):
    pval = stats.mannwhitneyu(gains[case1], gains[case2]).pvalue
    
    pt.annotate(inset, '%s vs %s: %s, p=%.1e ' % (case1, case2, pt.from_pval_to_star(pval), pval) + i*'\n',
                #'%s vs %s, %s, p=%.1e ' (case1, case2, pt.from_pval_to_star(pval), pval) + i*'\n',
               (0.5, 1.09), fontsize=6, ha='center')

pt.set_plot(inset, ['left'], ylabel='gain')

iFig +=1
fig.savefig(os.path.join(Fig_Folder, 'BM-%i.svg' % iFig))

# %% [markdown]
# ## Tuning Dependency

# %%
from physion.analysis.protocols.orientation_tuning import compute_tuning_response_per_cells,\
                        fit_gaussian, shift_orientation_according_to_pref

# %%
Responses = {}

contrast = 1.

speed_threshold = 0.1 # cm/s

Nmin_episodes = 3

dFoF_parameters = dict(\
        roi_to_neuropil_fluo_inclusion_factor=1.15,
        neuropil_correction_factor = 0.7,
        method_for_F0 = 'sliding_percentile',
        percentile=5., # percent
        sliding_window = 5*60, # seconds
)

stat_test_props=dict(interval_pre=[-1.,0],                                   
                   interval_post=[1.,2.],                                   
                   test='anova',                                            
                   positive=True)

response_significance_threshold=5e-2

cases, colors = DATASET.keys(), ['tab:orange', 'tab:purple', 'tab:green']

Angles = [-22.5, 0.0, 22.5, 45.0, 67.5, 90.0, 112.5, 135.0]

for i, case in enumerate(cases):

    # initialize the array of responses with respect to prefered orientation
    for label in ['rest', 'run']:
        Responses[case] = []
        for angle in Angles:
            Responses['%s_%s' % (case, label)] = []
            #Responses['%s_%s_%.1f_traces' % (case, label, angle)] = []

    # loop over datafiles
    for n, f in enumerate(DATASET[case]['files']):
        
        print(' - analyzing file # %i: %s  [...] ' % (n+1, f))
        data = Data(f, verbose=False)
        data.build_dFoF(**dFoF_parameters, verbose=False)

        Episodes = EpisodeData(data, 
                            quantities=['dFoF', 'running_speed'],
                            protocol_name=[p for p in data.protocols if 'ff-gratings' in p][0],
                            verbose=False, prestim_duration=3,
                            dt_sampling=10)

        # compute Run vs Rest :
        withinEpisode_cond = (Episodes.t>0) & (Episodes.t<Episodes.time_duration[0])
        Ep_run_speed = Episodes.running_speed[:,withinEpisode_cond].mean(axis=1)
        run = Ep_run_speed>=speed_threshold

        # find overall tuning (i.e. on all data irrespective of rest/run)
        resp = compute_tuning_response_per_cells(data, Episodes,
                                                 stat_test_props,
                                                 response_significance_threshold=response_significance_threshold,
                                                 contrast = contrast,
                                                 start_angle=-22.5, angle_range=180)
        Responses[case].append(np.mean([r/r[1] for r in resp['Responses'][resp['significant_ROIs']]], axis=0))
                               
        pre_window = (Episodes.t>stat_test_props['interval_pre'][0]) & (Episodes.t<stat_test_props['interval_pre'][1])
        post_window = (Episodes.t>stat_test_props['interval_post'][0]) & (Episodes.t<stat_test_props['interval_post'][1])

        # initialize session quantities
        sResp = {}
        for label in ['rest', 'run']:
            for angle in Angles:
                # we initialize a nROIs array of inf values that we will fill if the information is there
                sResp['%s_%s_%.1f' % (case, label, angle)] = np.ones(data.nROIs)*np.nan
                # we initialize a nROIs array of inf values that we will fill if the information is there
                sResp['%s_%s_%.1f_trace' % (case, label, angle)] = np.ones((data.nROIs, len(Episodes.t)))*np.nan
                
        # now loop over ROIs and split rest vs run
        for roi in np.arange(data.nROIs)[resp['significant_ROIs']]:

            max_resp = np.max(resp['Responses'][roi])
            
            for angle in Episodes.varied_parameters['angle']:

                shifted_angle = shift_orientation_according_to_pref(angle,
                                                                    pref_angle=resp['prefered_angles'][roi],
                                                                    start_angle=-22.5, angle_range=180)

                for cond, label in zip([~run, run], ['rest', 'run']):
                    
                    full_cond = (Episodes.contrast==contrast) & (Episodes.angle==angle) & cond
                    if np.sum(full_cond)>=Nmin_episodes:
                        # if at least 2 episodes, we fill the array
                        pre = Episodes.dFoF[full_cond, roi, :].mean(axis=0)[pre_window].mean()
                        post = Episodes.dFoF[full_cond, roi, :].mean(axis=0)[post_window].mean()
                        sResp['%s_%s_%.1f' % (case, label, shifted_angle)][roi] = (post-pre)/max_resp
                        # and we keep the mean trace :
                        sResp['%s_%s_%.1f_trace' % (case, label, shifted_angle)][roi,:] = \
                                                            Episodes.dFoF[full_cond, roi, :].mean(axis=0)

        # add the session average to the summary data
        for label in ['rest', 'run']:
            Responses['%s_%s' % (case, label)].append(\
                [np.nanmean([sResp['%s_%s_%.1f' % (case, label, angle)][roi] for roi in range(data.nROIs)])\
                                                 for angle in Angles])
    Responses['shifted_angles'] = Angles
    Responses['t'] = Episodes.t

# %%
# plot

fig, AX = pt.figure(axes=(3,1))
inset = pt.inset(AX[-1], [1.8, 0.2, 0.6, 1.])

x = np.linspace(-30, 180-30, 100)

cases = ['GluN1KO', 'WT', 'GluN3KO']
COLORS = ['tab:purple', 'darkorange', 'tab:green']

for i, case in enumerate(cases):
    
    pt.scatter(Responses['shifted_angles'], np.mean([r for r in Responses[case] if type(r)==np.ndarray], axis=0), color='k', ax=AX[i], ms=1)
    C, func = fit_gaussian(np.array(Responses['shifted_angles']), np.mean([r for r in Responses[case] if type(r)==np.ndarray], axis=0))
    AX[i].plot(x, func(x), lw=1, alpha=.2, color='k')
    
    for j, label, color in zip(range(2), ['rest', 'run'], ['tab:blue', 'tab:red']):

        pt.scatter(Responses['shifted_angles'], np.nanmean(Responses['%s_%s' % (case, label)], axis=0),
                   sy=np.nanstd(Responses['%s_%s' % (case, label)], axis=0)/np.sqrt(len(Responses['%s_%s' % (case, label)],)),
                   color=color, ax=AX[i], ms=2)
        C, func = fit_gaussian(np.array(Responses['shifted_angles']), 
                               np.array(np.nanmean(Responses['%s_%s' % (case, label)], axis=0)))
        AX[i].plot(x, func(x), lw=2, alpha=.5, color=color)
        pt.bar([1-C[2]/(C[0]+C[2])], x=[i+j/3.], width=.25, ax=inset, color=color)
        
    pt.set_plot(AX[i], xlabel='angle ($^o$) from pref.', 
                ylabel='norm. $\Delta$F/F',
                xticks=Responses['shifted_angles'],
                xticks_labels=['%.0f'%s if (s%90==0) else '' for s in Responses['shifted_angles']])
    AX[i].set_title('%s\n(N=%i sessions)' % (case, len(Responses['%s_%s' % (case, label)])), color=COLORS[i])
    inset.annotate(case, (i+.2,0), xycoords='data', va='top', ha='center', rotation=90, color=COLORS[i])

pt.annotate(inset, 'rest', (0,1), color='tab:blue')
pt.annotate(inset, 'run', (1,1), ha='right', color='tab:red')
pt.set_plot(inset, ['left'], ylabel='selectivity index')
pt.set_common_ylims(AX)

iFig +=1
fig.savefig(os.path.join(Fig_Folder, 'BM-%i.svg' % iFig))

# %%
