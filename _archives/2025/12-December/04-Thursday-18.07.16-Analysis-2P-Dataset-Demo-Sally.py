# %%
import numpy as np

import sys, os
sys.path += ['physion/src']
import physion

from physion.analysis.read_NWB import Data
from physion.analysis.process_NWB import EpisodeData

import physion.utils.plot_tools as pt
pt.set_style('dark')

folder = os.path.expanduser('~/DATA/Sally/PYR_WT_V1-demo-2P-2025')

dataset, subjects, _ = physion.assembling.dataset.read_spreadsheet(\
                                    os.path.join(folder, 'DataTable.xlsx'))

DS = physion.analysis.read_NWB.scan_folder_for_NWBfiles(\
                                        os.path.join(folder, 'NWBs'))

# BUILD PROTOCOL NAMES (see generate_protocol_visual_features_variations.py script)
import itertools
STRs = []
for spatial, temporal, contrast, size in itertools.product(\
   ['smpl', 'cmplx'], ['fix', 'dyn'], ['lC', 'hC'], ['smll','lrg']):
    protocol = '%s-%s-%s-%s' % (spatial, temporal, contrast, size) 
    STRs.append(protocol)

# %%

dFoF_options = {
    'method_for_F0':'sliding_percentile',
}

RUNNING_SPEED_THRESHOLD = 0.5


stat_test_props = dict(interval_pre=[-1.,0],   # both
                       interval_post=[1.,2.],  # updated                                  
                       test='ttest',                                            
                       sign='positive')

response_significance_threshold = 0.01 # very very conservative

# %%

def process(data):

    Significants = {}
    for i, p in enumerate(data.protocols):

        ep = EpisodeData(data, 
                         quantities=['dFoF', 'running_speed'],
                         protocol_name=p)
        key = list(ep.varied_parameters.keys())[0] 

        for j in range(2):
            Significants['%s-%s-%s' % (p, key, j+1)] = np.zeros(data.nROIs,
                                                               dtype=bool)
        # update interval
        stat_test_props['interval_pre'] = [-ep.time_duration[0], 0]
        stat_test_props['interval_post'] = [0, ep.time_duration[0]]

        for roi in range(data.nROIs):

            summary = ep.compute_summary_data(stat_test_props,
                                    response_args={'quantity':'dFoF',
                                                   'roiIndex':roi},
                                    response_significance_threshold=response_significance_threshold)

            for j in range(2):
                Significants['%s-%s-%s' % (p, key, j+1)][roi] = summary['significant'][j]

    return Significants
                                    
data = Data(DS['files'][0])
data.build_dFoF(**dFoF_options)
data.build_running_speed()

Significants = process(data)

# %%
def plot_episodes(data, Significants,
                  runColor='tab:blue', restColor='tab:orange',
                  N=6):

    fig, AX = pt.figure(axes=(4,8), ax_scale=(1,1.5), 
                        hspace=0.5, wspace=0.8)

    for i, p in enumerate(data.protocols):

        ep = EpisodeData(data, 
                         quantities=['dFoF', 'running_speed'],
                         prestim_duration=1,
                         protocol_name=p)
        
        withinEpisode = (ep.t>0) & (ep.t<ep.time_duration[0])
        run = np.mean(\
            ep.running_speed[:,withinEpisode],
                        axis=1) > RUNNING_SPEED_THRESHOLD

        key = list(ep.varied_parameters.keys())[0] 


        for j in range(2):
            # 2 stims

            ax = AX[2*int(i/4)+j][int(i%4)]
            ax.axis('off')

            significants = np.arange(data.nROIs)[\
                                Significants['%s-%s-%s' % (p, key, j+1)]]

            if len(significants)>0:
                rois = np.random.choice(\
                                    np.arange(data.nROIs)[significants], 
                                    min([N, len(significants)]),
                                    replace=False)
                
                insets = [pt.inset(ax, [0, k/N, 1, 1/N])\
                        for k in range(len(rois))]
                
                for k, r in enumerate(rois):

                    pt.plot(ep.t, ep.dFoF[run, r, :].mean(axis=0),
                            sy=ep.dFoF[run, r, :].std(axis=0),
                            lw=0.5, ax = insets[k], color=runColor)
                    pt.plot(ep.t, ep.dFoF[~run, r, :].mean(axis=0),
                            sy=ep.dFoF[~run, r, :].std(axis=0),
                            lw=0.5, ax = insets[k], color=restColor)

                    pt.draw_bar_scales(insets[k], lw=0.5,
                                      Xbar=1, 
                                      Xbar_label='1s' if (i+j+k)==0 else '',
                                      Ybar=1,
                                      Ybar_label='1$\\Delta$F/F' if (i%4+k)==0 else '')
                    insets[k].axis('off')

            pt.set_plot(ax,
                        xlabel='time (s)' if int(i/4)==7 else '')
            pt.annotate(ax, '%s-%i' % (STRs[i],j), (0.5,1), ha='center')

    pt.set_common_ylims(AX)
    pt.set_common_xlims(AX)

    return fig, AX

fig, AX = plot_episodes(data, Significants)

# %%
for n, f in enumerate(DS['files']):
    data = Data(f)
    data.build_dFoF(**dFoF_options)
    data.build_running_speed()
    Significants = process(data)
    fig, AX = plot_episodes(data, Significants)
    pt.annotate(AX[-1][-1], str(n)+') '+data.filename, (0, 0), va='top')

# %%
