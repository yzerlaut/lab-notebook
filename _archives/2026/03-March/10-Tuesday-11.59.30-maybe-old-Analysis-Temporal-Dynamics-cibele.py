import sys, os
sys.path += ['physion/src']
import physion.utils.plot_tools as pt
from scipy import stats
from physion.dataviz.episodes.temporal_dynamics\
        import plot_response_dynamics

summary_folder = os.path.join(os.path.expanduser('~'), 
                            'CURATED', 'Cibele', 'summary')
folders = [
    "PV-cells_WT_Adult_V1", 
    "PV-cells_WT_Young_V1",
    "PV-cells_cond-GluN1-KO_Adult_V1", 
    "PYR-PV-SynGCaMP_WT_Young_V1",
    "SST-cells_cond-GluN1-KO_Young_V1",
    "SST-cells_WT_Adult_V1",
    "SST-cells_WT_Young_V1",
    "SST-cells_cond-GluN1-KO_Adult_V1_Taddy",
    "SST-cells_WT_Adult_V1_Taddy"
]

for i, folder in enumerate(folders):
    fig, ax = plot_response_dynamics(\
                            ['%s_contrast-0.5' % folder, 
                                '%s_contrast-1.0' % folder],
                            # average_by='ROIs',
                            significantly_responsive=False,
                            colors = ['lightgrey', pt.tab10(i)],
                            path=summary_folder)

# %%
import numpy as np

folders = [
    "PV-cells_WT_Adult_V1", 
    "SST-cells_WT_Adult_V1",
]

baseline_window = [-1., 0.]
peak_window = [0., 1.]
late_window = [0.8, 2.]

# fig, ax = pt.figure()

labels, values = [], []

for i, folder in enumerate(folders):

    Responses = np.load(\
        os.path.join(summary_folder,
                     'Deconvolved_%s_contrast-1.0.npy' % folder),
                     allow_pickle=True)

    Deconvolved = [np.mean(Response['Deconvolved'][Response['significant'],:],
                    axis=0) for Response in Responses\
                        if np.sum(Response['significant'])>0]

    t = Responses[0]['t']


    baseline_cond = (t>baseline_window[0]) &\
                        (t<baseline_window[1])
    Deconvolved = np.array([d-d[baseline_cond].mean()\
                             for d in Deconvolved])

    peak_cond = (t>peak_window[0]) & (t<peak_window[1])
    Deconvolved = np.array([d/d[peak_cond].max()\
                             for d in Deconvolved])

    late_cond = (t>late_window[0]) & (t<late_window[1])

    values.append(\
        np.array([d[late_cond].mean()\
                                for d in Deconvolved]))

    labels.append(folder.split('_')[0].split('-')[0])

    print()
    print(labels[-1])
    for v in values[-1]:
        print(v)
    