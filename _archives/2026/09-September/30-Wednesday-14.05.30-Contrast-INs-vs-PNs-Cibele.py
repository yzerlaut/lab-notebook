# %%
import sys, os
sys.path += ['physion/src']
import physion.utils.plot_tools as pt
from physion.analysis.protocols.contrast_sensitivity\
        import plot_contrast_sensitivity, plot_contrast_responsiveness
import numpy as np

summary_folder =\
        os.path.expanduser('~/CURATED/Cibele/summary')

fig_folder = os.path.expanduser(\
    '~/Documents/Notebook/Projects/Cibele-PhD/summary-data-Dec2025/figures/Fig2')
if not os.path.isdir(fig_folder):
    fig_folder = os.path.expanduser('~/Desktop/') # by default
    
iFig = 1
def save(fig, format='svg'):
    global iFig
    fig.savefig(os.path.join(fig_folder, '%i.%s' % (iFig, format)))
    iFig +=1

pt.set_style('dark')

# %%
folders = [
    "PV-cells_WT_Adult_V1", 
    "SST-cells_WT_Adult_V1",
    "PYR-SynGCaMP_WT_Adult_V1",
]
colors = [
    "tab:red",
    "tab:orange",
    "tab:blue",
]

Folders = ['%s_angle-0.0' % folder for folder in folders]

average_by = 'sessions'

for average_by in ['sessions', 'ROIs']:
    fig, ax = plot_contrast_sensitivity(Folders,
                            average_by=average_by,
                            colors = colors,
                            path=summary_folder)
    save(fig)
fig, ax = plot_contrast_responsiveness(Folders,
                        colors = colors,
                        sign='positive',
                        path=summary_folder)
save(fig)
fig, ax = plot_contrast_responsiveness(Folders,
                        colors = colors,
                        sign='negative',
                        path=summary_folder)
save(fig)


# %%
# checking cell numbers in summary data:
for f in Folders:
    print()
    print(f)
    Sensitivities = \
        np.load(os.path.join(summary_folder, 
                             'Sensitivities_%s.npy' % f), 
                allow_pickle=True)
    for i, s in enumerate(Sensitivities):
        s['resp+'] = np.sum(s['significant_pos'][:,-1]) # at full-contrast
        s['resp-'] = np.sum(s['significant_neg'][:,-1])
        print('session:', i+1, ' ) ROIs --> original: %(nROIs_original)i, valid:%(nROIs_original)i, resp+:%(resp+)i, resp-:%(resp-)i' % s)

    
# %%