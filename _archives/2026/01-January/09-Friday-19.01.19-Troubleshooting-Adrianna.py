# %%
import numpy as np
import os, sys
sys.path.append('physion/src') # add src code directory for physion
import physion
import physion.utils.plot_tools as pt
pt.set_style('dark')

dFoF_options = dict(\
    method_for_F0='percentile', # static
    percentile=10,
    neuropil_correction_factor=0.7, 
    with_computed_neuropil_fact=False,
    roi_to_neuropil_fluo_inclusion_factor=1.)

stat_test_props = dict(interval_pre=[-1.,0],                                   
                       interval_post=[0.5,1.5],                                   
                       test='ttest')

response_significance_threshold = 0.05

# load file and build modalities:
filename = os.path.expanduser(\
      '~/DATA/Adrianna/PN_cond-NDNF-CB1_WT-vs-KD/NWBs/2025_09_16-17-49-49.nwb')
data = physion.analysis.read_NWB.Data(filename)
data.build_dFoF(**dFoF_options, verbose=True)
data.build_pupil_diameter()
data.build_facemotion()
data.build_running_speed()

# load episodes (/trials) of a given protocol within the recording
epGrating = physion.analysis.episodes.build.EpisodeData(data, 
                                    quantities=['dFoF', 'running_speed'],
                                    protocol_name='drifting-grating')


summary = epGrating.pre_post_statistics(\
                stat_test_props,
                # episode_cond =contrast_cond,
                response_args=dict(quantity='dFoF',
                                    roiIndex=0), #np.arange(data.nROIs)),
                response_significance_threshold=response_significance_threshold,
                multiple_comparison_correction=False,
)
print(summary)
# %%
summary = epGrating.pre_post_statistics_over_cells(\
                stat_test_props,
                # episode_cond =contrast_cond,
                response_args=dict(quantity='dFoF',
                                    roiIndex=0), #np.arange(data.nROIs)),
                response_significance_threshold=response_significance_threshold,
                multiple_comparison_correction=False,
)
print(summary)

# %%
print(summary)

# split rest / run episodes
RUNNING_SPEED_THRESHOLD = 0.1 # cm/s
withinEpisode = (epGrating.t>0) & (epGrating.t<epGrating.time_duration[0])
run = np.mean(epGrating.running_speed[:,withinEpisode], axis=1) > RUNNING_SPEED_THRESHOLD

summary = epGrating.pre_post_statistics(\
                stat_test_props,
                episode_cond = run,
                response_args=dict(quantity='dFoF',
                                    roiIndex=0), #np.arange(data.nROIs)),
                response_significance_threshold=response_significance_threshold,
                multiple_comparison_correction=False,
)
summary

# %%

# PLOT PROPERTIES --- DRIFTING GRATINGS ---

plot_props = dict(column_key='contrast',
                  with_annotation=True,
                  Ybar=0.5, Ybar_label="0.5$\Delta$F/F",
                  Xbar=0.5, Xbar_label="0.5s",
                  figsize=(9,1.8))


# RESPONSE ARGUMENTS --- DRIFTING GRATINGS ---



response_args = dict(quantity='dFoF')

summary_stats = []

NMIN_EPISODES = 2
NMIN_ROIS = 3

# %%
means = {} # 
for virus in ['sgRosa', 'sgCnr1']:
      for cond in ['all', 'run', 'still']:
              for c, contrast in enumerate([0.2, 0.6, 1.0]):
                means['%s-%s-c=%.1f' % (virus, cond, contrast)] = []


for i, filename in enumerate(DATASET['files'][5:6]):
    
    data = physion.analysis.read_NWB.Data(filename,
                                    verbose=False)
    
    print(i+1, '--', filename, '--', data.nROIs)
    # print(data.protocols)

    data.build_dFoF(**dFoF_options, verbose=True)
    data.build_pupil_diameter()
    data.build_facemotion()
    data.build_running_speed()
    
    if data.nROIs>0:

        epGrating = physion.analysis.episodes.build.EpisodeData(data, 
                                                        quantities=['dFoF', 'running_speed'],
                                                        protocol_name='drifting-grating')

        # determine virus        
        if 'sgRosa' in data.nwbfile.virus:
                virus = 'sgRosa'
        elif 'sgCnr1':
                virus = 'sgCnr1'


        # find significant ROIs (for each contrast)
        for c, contrast in enumerate([0.2, 0.6, 1.0]):

                contrast_cond = epGrating.find_episode_cond(key='contrast',
                                                            index=c)

                significant = np.zeros(data.nROIs, dtype=bool)
                for n in range(data.nROIs)[:1]:
                        summary = epGrating.compute_summary_data(\
                                        stat_test_props,
                                        episode_cond =contrast_cond,
                                        response_args=dict(quantity='dFoF',
                                                           roiIndex=n),
                                        response_significance_threshold=response_significance_threshold,
                        )
                        print(summary)
                        significant[n] = np.sum(summary['significant'])

                for cond, filter in zip(['all', 'run', 'still'],
                                        [run|~run, run, ~run]):

                        means['%s-%s-c=%.1f' % (virus, cond, contrast)].append(
                                epGrating.dFoF[contrast_cond & run, :, :][:, significant, :]
                                )
                        
# %%
