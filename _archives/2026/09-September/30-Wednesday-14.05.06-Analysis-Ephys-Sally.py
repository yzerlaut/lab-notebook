# %%
import os, sys
import pandas as pd
import numpy as np

sys.path += ['physion/src']

from physion.analysis.read_NWB import Data,\
                    scan_folder_for_NWBfiles 
from physion.analysis.episodes.build import EpisodeData

import physion.utils.plot_tools as pt
from physion.dataviz.episodes.evoked_pattern\
         import plot as plot_evoked_pattern
from physion.dataviz.episodes.trial_average\
    import plot as plot_trial_average

# %%
datafolder = os.path.join(os.path.expanduser('~'), 
                    'DATA', 'Sally', '2026_06_09')

DATASET = scan_folder_for_NWBfiles(datafolder) 

# %%
# datafile = os.path.join(datafolder,
#         # '2026_06_09-17-34-41.nwb')
#         '2026_06_09-17-25-06.nwb')
datafile = DATASET['files'][0]
data = Data(datafile)
data.build_MUA()

# %%
data.build_spikes()

# %%
ep = EpisodeData(data, 
                 dt_sampling=5, # ms
                 quantities=['MUA'],
                #  quantities=['spikes'],
                 protocol_id=0)

# %%
plot_evoked_pattern(ep, quantity='spikes')
# pt.plt.show()
# %%
fig, AX = pt.figure(axes=(1,2), 
                    ax_scale=(1.5,2),
                    hspace=0.1)

electrode_subsampling = 2

norm = ep.MUA[:,:,ep.t<0].mean(axis=(0,2))
AX[0].imshow(np.transpose(ep.MUA.mean(axis=0).T/norm),
           aspect='auto', interpolation='none',
            #    vmin=0, vmax=2, 
               origin='lower',
            extent = (ep.t[0], ep.t[-1], 
                      0, electrode_subsampling*ep.MUA.shape[1]))

pt.plot(ep.t, ep.MUA.mean(axis=(0,1)), 
        # sy=np.std(ep.MUA.mean(axis=1), axis=0),
        ax=AX[1])
for ax in AX:
    pt.set_plot(ax, 
                xlim=[ep.t[0], ep.t[-1]])
                # xlim=[-0.15, 1.1])
AX[0].set_title('(baseline-normed) MUA')
AX[0].set_ylabel('channel ID')
AX[1].set_ylabel('MUA ($\mu$V)\n channel-average')
AX[1].set_xlabel('time from stim. (s)')

# %%
datafile = DATASET['files'][1]
data = Data(datafile)
data.build_MUA()

# %%
ep = EpisodeData(data, 
                 dt_sampling=5, # ms
                 quantities=['MUA'],
                 protocol_id=0)
# %%
stat_test_props=dict(interval_pre=[-0.5,0],
        interval_post=[0.2,0.7],
        test='ttest',
        sign='positive')

fig, AX = plot_trial_average(ep, 
                quantity='MUA',
                smoothing=2,
                row_key='y-center',
                column_key='x-center',
                # with_std=False,
                with_stat_test=True,
                stat_test_props=stat_test_props,
                Xbar=0.5, Xbar_label='500ms',
                Ybar=10, Ybar_label='10$\mu$V',
                screen_inset=[.6, .7, .7, .4],
                ylim=[40, 80],
                with_screen_inset=True)


# %%
datafile = DATASET['files'][2]
data = Data(datafile)
data.build_MUA()

# %%
ep = EpisodeData(data, 
                 dt_sampling=5, # ms
                 quantities=['MUA'],
                 protocol_id=0)
# %%
stat_test_props=dict(interval_pre=[-0.5,0],
        interval_post=[0.3,0.8],
        test='ttest',
        sign='positive')

fig, AX = plot_trial_average(ep, 
                quantity='MUA',
                smoothing=2,
                row_key='y-center',
                column_key='x-center',
                # with_std=False,
                with_stat_test=True,
                stat_test_props=stat_test_props,
                Xbar=0.5, Xbar_label='500ms',
                Ybar=10, Ybar_label='10$\mu$V',
                screen_inset=[.6, .7, .7, .4],
                ylim=[40, 80],
                with_screen_inset=True)

# %%

fig, AX = pt.figure(axes=(1,2), 
                    ax_scale=(1.5,2),
                    hspace=0.1)

electrode_subsampling = 2

norm = ep.MUA[:,:,ep.t<0].mean(axis=(0,2))
AX[0].imshow(np.transpose(ep.MUA.mean(axis=0).T/norm),
           aspect='auto', interpolation='none',
            #    vmin=0, vmax=2, 
            #    origin='lower',
            extent = (ep.t[0], ep.t[-1], 
                      0, electrode_subsampling*ep.MUA.shape[1]))

pt.plot(ep.t, ep.MUA.mean(axis=(0,1)), 
        # sy=np.std(ep.MUA.mean(axis=1), axis=0),
        ax=AX[1])
for ax in AX:
    pt.set_plot(ax, 
                # xlim=[ep.t[0], ep.t[-1]])
                xlim=[-0.15,1.1])
AX[0].set_title('(baseline-normed) MUA')
AX[0].set_ylabel('channel ID')
AX[1].set_ylabel('MUA ($\mu$V)\n channel-average')
AX[1].set_xlabel('time from stim. (s)')

# %%
if False:

    datafile = os.path.join(os.path.expanduser('~'), 
            'DATA', 'Sally', 
            '2026_04_24-12-45-49.nwb')

    data = Data(datafile)
    data.build_spikes()
    data.build_opto()
    ep = EpisodeData(data, 
                    dt_sampling=5, # ms
                    quantities=['spikes', 'opto'],
                    protocol_id=0)


# %%
if True:

    from physion.dataviz.episodes.trial_average\
        import plot as plot_trial_average

    stat_test_props=dict(interval_pre=[-0.5,0],
                    interval_post=[0.3,0.8],
                    test='wilcoxon',
                    sign='positive')

    datafile = os.path.join(os.path.expanduser('~'), 
            'DATA', 'Sally', '2026_06_09',
            '2026_06_09-17-30-59.nwb')

    data = Data(datafile)
    data.build_MUA()
    ep = EpisodeData(data, 
                    dt_sampling=20, # ms
                    quantities=['MUA'],
                    protocol_id=0)
# %%
if True:
    fig, AX = plot_trial_average(ep, 
                    quantity='MUA',
                    smoothing=8,
                    row_key='y-center',
                    column_key='x-center',
                    with_std=True,
                    with_stat_test=True,
                    stat_test_props=stat_test_props,
                    Xbar=0.5, Xbar_label='500ms',
                    Ybar=10, Ybar_label='10$\mu$V',
                    screen_inset=[.7, .9, .4, .3],
                    # ylim=[45, 70],
                    with_screen_inset=True)
# %%
if False:
    datafile = os.path.join(os.path.expanduser('~'), 
            'DATA', 'Sally', '2026_06_09', 
            '2026_06_09-17-34-41.nwb')

    from physion.dataviz.episodes.trial_average\
        import plot as plot_trial_average

    stat_test_props=dict(interval_pre=[-0.8,0],
                    interval_post=[0.2,1],
                    test='wilcoxon',
                    sign='positive')

# %%
# loop over units
if False:
    for i in range(ep.spikes.shape[1]):

        stat = ep.pre_post_statistics(\
            response_args=dict(quantity='spikes', index=i),
            multiple_comparison_correction=False,
            stat_test_props=stat_test_props,
            verbose=False)
        
        # if at least one significant
        if np.sum(stat['significant'])>0:
            fig, AX = plot_trial_average(ep, 
                            quantity='spikes',
                            index=i,
                            smoothing=4,
                            row_key='y-center',
                            column_key='x-center',
                            with_std=False,
                            with_stat_test=True,
                            stat_test_props=stat_test_props,
                            Xbar=0.5, Xbar_label='500ms',
                            Ybar=1e-2, Ybar_label='0.1Hz',
                            screen_inset=[.7, .9, .4, .3],
                            with_screen_inset=True)
            pt.annotate(AX[-1][0], '\nunit #%i' % (i+1), (-0.2, 0),
                        ha='right', rotation=90, fontsize=8)

# %%