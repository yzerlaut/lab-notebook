# %%
# general python modules for scientific analysis
import sys, pathlib, os
import numpy as np

sys.path += ['physion/src'] # add src code directory for physion
from physion.utils import plot_tools as pt

from physion.analysis.read_NWB import Data,\
    scan_folder_for_NWBfiles

# default plot
from physion.dataviz.raw import plot as plot_raw
from physion.dataviz.imaging import show_CaImaging_FOV
pt.set_style('dark')

# %%
folder = os.path.join(os.path.expanduser('~'), 
            'DATA', 'Taddy', 'PN_shGrid1-2026', 'NWBs')

notebook_folder =\
    os.path.join(os.path.expanduser('~'), 
        'OneDrive - ICM', 'Lab-Notebook', 'Data')

redo_figs = True

# %%
dataset = scan_folder_for_NWBfiles(\
        os.path.join(os.path.expanduser('~'), 
            'DATA', 'Taddy', 'PN_shGrid1-2026'),
            for_protocol='plasticity-60'
            )

# %%
quantity = 'dFoF'
dFoF_parameters = dict(\
    roi_to_neuropil_fluo_inclusion_factor=0., # no factor here
    neuropil_correction_factor = 0.5,
    # with_computed_neuropil_fact=True, 
    method_for_F0 = 'sliding_percentile',
    percentile=10., # percent
    sliding_window = 5*60, # seconds
)
# %%

def single_rec(filename):

    print('running %s' % filename)
    fn = os.path.basename(filename).replace('.nwb', '')

    md = os.path.join(notebook_folder, fn+'.md')

    text = '## Recording \n\n'
    text = '-  %s \n ' % fn
    data = Data(filename)
    if data.has_visual_stim():
        data.build_visual_stim() # real recording (possibly stopped)
        nReal = data.visual_stim.experiment['time_start'].shape[0]
        # we rebuild a full experiment
        data.visual_stim.init_experiment(data.visual_stim.protocol,
                                        data.visual_stim.protocol)
        nFull = data.visual_stim.experiment['time_start'].shape[0]
        data.build_visual_stim() # back to real recording 
        text += '- episodes: %i / %i   \n' % (nReal, nFull)
    text += '\n'

    text += '### mouse \n\n'
    text += '- ID: %s  \n' % data.nwbfile.subject.subject_id
    text += '- virus: %s \n' % data.nwbfile.virus
    text += '- genotype/strain : %s / %s \n' %\
         (data.nwbfile.subject.genotype, data.nwbfile.subject.strain)
    text += '- age @rec: %s  \n' % data.nwbfile.subject.age
    text += '- DOB: %s  \n' % data.nwbfile.subject.date_of_birth.strftime('%Y-%m-%d')
    text += ' \n \n'

    text += '### Protocol (%s) \n\n' % data.metadata['protocol']
    for p in data.protocols:
        text += '- %s \n' % p
    text += ' \n'


    if redo_figs:
        data.build_dFoF(**dFoF_parameters)


    text += '## Field of View \n'

    if redo_figs:
        fig, AX = pt.figure(axes=(3,1), ax_scale=(1.3,2.6), 
                            top=0.05, bottom=0.05, wspace=0.1)

        #
        show_CaImaging_FOV(data, key='meanImg', 
                        cmap=pt.get_linear_colormap('k', 'tab:green'),
                        NL=3, # non-linearity to normalize image
                        with_annotation=True,
                        ax=AX[0])
        show_CaImaging_FOV(data, key='max_proj', 
                        cmap=pt.get_linear_colormap('k', 'tab:green'),
                        NL=3, # non-linearity to normalize image
                        with_annotation=False, ax=AX[1])
        show_CaImaging_FOV(data, key='meanImg', 
                        cmap=pt.get_linear_colormap('k', 'tab:green'),
                        NL=3,
                        roiIndex=range(data.nROIs), 
                        with_annotation=False, ax=AX[2])
        pt.save(fig, os.path.join(notebook_folder, 'figs'), 
                fn+'-FOV.svg', dpi=75)

    text += '![](figs/%s)    \n \n' % (fn+'-FOV.svg')

    def get_settings(subsampling_factor=1,
                     with_visual_stim=False):
        settings = {}

        if data.has_running():
            settings['running'] = {'fig_fraction': 1,
                                    'subsampling': 5*subsampling_factor,
                                    'color': '#1f77b4'}
        if data.has_facemotion():
            settings['facemotion'] = {'fig_fraction': 1,
                                        'subsampling': 2*subsampling_factor,
                                        'color': 'purple'}
        if data.has_pupil():
            settings['pupil'] = {'fig_fraction': 2,
                                    'subsampling': 2*subsampling_factor,
                                    'color': '#d62728'}

        settings['CaImaging'] = {'fig_fraction': 15,
                                'subsampling': 1*subsampling_factor,
                                'subquantity': 'dF/F',
                                # 'subquantity': 'rawFluo',
                                'roiIndices': np.random.choice(np.arange(data.nROIs), np.min([40,data.nROIs]), replace=False),
                                'color': '#2ca02c'}

        if with_visual_stim:
            settings['photodiode']= {'color': 'lightgrey', 'fig_fraction': 0.5, 
                                     'subsampling': 10*subsampling_factor}
            settings['visual_stim']= {'color': 'w', 'fig_fraction': 0.5}

        return settings

    # full recording view
    if redo_figs:
        fig, AX = \
            plot_raw(data, 
                    tlim=[0, data.t_dFoF[-1]], 
                    settings=get_settings(subsampling_factor=20),
                    fig_args=dict(ax_scale=(2.5,25.), 
                                bottom=.02, top=.001, left=.3, right=.3))
        pt.save(fig, os.path.join(notebook_folder, 'figs'), 
                fn+'-full.svg')

    text += '## Full View: %.1fs (%.1fmin)     \n' % (data.tlim[1], data.tlim[1]/60.)
    text += '![](figs/%s)    \n \n' % (fn+'-full.svg')

    ## zoomed view
    for i, t0 in enumerate(\
        np.linspace(0, data.tlim[-1]-60,3)):
        if redo_figs:
            fig, AX = \
                plot_raw(data, 
                        tlim=[t0, t0+60],
                        settings=get_settings(with_visual_stim=True),
                        fig_args=dict(ax_scale=(2.5,20.), 
                                    bottom=.001, top=.15, left=.3, right=.3))
            pt.save(fig, os.path.join(notebook_folder, 'figs'), 
                    fn+'-%i.svg' % (i+1))

        text += '### Zoom %i : 1min @ %.1fmin (%.1fs)    \n' % (i+1, t0/60., t0)
        text += '![](figs/%s)    \n\n' % (fn+'-%i.svg' % (i+1))

    with open(md, 'w') as f:
        f.write(text)
    return text

text = single_rec(dataset['files'][0])
print(text)
# %%
if 1:
    for f in dataset['files']:
        _ = single_rec(f)
# %%
data = Data(dataset['files'][0])
data.build_visual_stim()
nReal = data.visual_stim.experiment['time_start'].shape[0]
data.visual_stim.init_experiment(data.visual_stim.protocol,
                                 data.visual_stim.protocol)
nFull = data.visual_stim.experiment['time_start'].shape[0]
data.build_visual_stim()
print(nReal, nFull)
# %%
