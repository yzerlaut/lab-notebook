# %%
import sys, os
sys.path += ['physion/src']
import physion.utils.plot_tools as pt
from physion.analysis.protocols.orientation_tuning\
        import plot_orientation_tuning_curve, plot_selectivity,\
                plot_selectivity_distrib

summary_folder =\
        os.path.expanduser('~/CURATED/Cibele/summary')

fig_folder = os.path.expanduser(\
    '~/Documents/Notebook/Projects/Cibele-PhD/summary-data-Dec2025/figures/Fig1')
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

average_by = 'sessions'
ALLs, COLORs = [], []
for i, folder in enumerate(folders):

    keys = ['%s_contrast-1.0' % folder, 
            '%s_contrast-0.5' % folder]
    Colors = [colors[i], 'lightgrey']

    fig, ax = plot_orientation_tuning_curve(keys,
                            average_by=average_by,
                            colors = Colors,
                            path=summary_folder)
    save(fig)

    ALLs += keys
    COLORs += Colors

for average_by in ['ROIs', 'sessions']:
    fig, ax = plot_selectivity(ALLs,
                            average_by=average_by,
                            #  using='fit',
                            colors = COLORs, 
                            path=summary_folder)
    save(fig)

# %%
average_by = 'ROIs'
import numpy as np
for contrast in [0.5, 1.0]:
    fig, ax = plot_selectivity_distrib(\
                                [\
                                    "PV-cells_WT_Adult_V1_contrast-%.1f" % contrast, 
                                    "SST-cells_WT_Adult_V1_contrast-%.1f" % contrast,
                                    "PYR-SynGCaMP_WT_Adult_V1_contrast-%.1f" % contrast,
                                ],
                                average_by=average_by,
                                plot='cum. frac.',
                                # plot='hist',
                                bins=np.linspace(0, .99, 40),
                                colors = colors,
                                path=summary_folder)
    ax.set_title('contrast = %.1f' % contrast)
    save(fig)

# %%
folders = [
    "PV-cells_WT_Adult_V1", 
    # "PV-cells_WT_Young_V1",
    # "PV-cells_cond-GluN1-KO_Adult_V1", 
    # "PYR-PV-SynGCaMP_WT_Young_V1",
    "PYR-SynGCaMP_WT_Adult_V1",
    # "SST-cells_cond-GluN1-KO_Young_V1",
    "SST-cells_WT_Adult_V1",
    # "SST-cells_WT_Young_V1",
    # "SST-cells_cond-GluN1-KO_Adult_V1_Taddy",
    # "SST-cells_WT_Adult_V1_Taddy"
]