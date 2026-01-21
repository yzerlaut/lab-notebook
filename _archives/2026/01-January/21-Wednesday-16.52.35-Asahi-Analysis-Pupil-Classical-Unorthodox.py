# %% [markdown]
# # Analysis of Asahi Protocols

# %%
import sys, os
sys.path += ['./physion/src']
import physion
from physion.utils import plot_tools as pt
pt.set_style('manuscript')

# %% [markdown]
# # Pupil Variations

# %%
folder = os.path.expanduser(\
    '~/DATA/Adrianna/Asahi-SepOct-2025/NWBs')
DATASET = \
    physion.analysis.read_NWB.scan_folder_for_NWBfiles(folder)


# %%
classical =\
    [p[0]=='Asahi-classical' for p in DATASET['protocols']]

stim_pics_folder = os.path.expanduser(\
    '~/Documents/Research/2025/Asahi-Design-Alberto/classical')

Nimages = 4
Responses = [[] for i in range(Nimages)]

for f in DATASET['files'][classical]:

    data = physion.analysis.read_NWB.Data(f)
    data.metadata['json_location'] = stim_pics_folder 
    data.init_visual_stim()
    data.build_pupil_diameter()

    if hasattr(data, 'pupil_diameter'):
        Episodes = \
    physion.analysis.episodes.build.EpisodeData(data,
                                                quantities=['pupil_diameter'],
                                                prestim_duration=2)

        for i in range(Nimages):
            iCond = Episodes.find_episode_cond(\
                            key='Image-ID', 
                            value=i+1)
            Responses[i].append(\
                Episodes.pupil_diameter[iCond,:].mean(axis=0))


# %%
fig2, aX = pt.figure(ax_scale=(1.2,1.2))
fig, AX = pt.figure((Nimages,2))

Labels = ["Asahi", "Gradient-Reversed", "Gradient-Alternated", "Center-0.5-contrast"]
COLORS = ['tab:red', 'tab:blue', 'tab:green', 'tab:purple']

from scipy import stats
import numpy as np

for i in range(Nimages):
    inset = pt.inset(AX[0][i], [0.1,1.,0.8,0.8])
    iStim = np.flatnonzero(\
        np.array(data.visual_stim.experiment['Image-ID'])==(i+1))[0] 
    pt.matrix(data.visual_stim.get_image(iStim),
              colormap=pt.gray, vmin=0, vmax=1, ax=inset)
    inset.axis('off')
    inset.set_title(Labels[i], fontsize=6, color=COLORS[i])
    pt.annotate(aX, i*'\n'+Labels[i], (1,1), va='top', color=COLORS[i])

    pt.plot(Episodes.t, np.mean(Responses[i], axis=0), 
            sy=stats.sem(Responses[i], axis=0),
            ax=AX[0][i], color=COLORS[i])

    norm_resp = [(resp-np.mean(resp[Episodes.t<0]))/np.mean(resp[Episodes.t<0]) for resp in Responses[i]]

    pt.plot(Episodes.t, 100*np.mean(norm_resp, axis=0), 
            sy=100*stats.sem(norm_resp, axis=0),
            ax=AX[1][i], color=COLORS[i])
    aX.plot(Episodes.t, 100*np.mean(norm_resp, axis=0), color=COLORS[i])

    pt.set_plot(AX[0][i], xticks=[-2,0,2,4], 
                ylabel='pupil diam.\n(mm)' if i==0 else '')
    pt.set_plot(AX[1][i], xticks=[-2,0,2,4], xlabel='time (s)',
                ylabel='norm. pupil\n(% baseline)' if i==0 else '')

pt.set_common_ylims(AX[0])
pt.set_common_ylims(AX[1])

for ax in list(pt.flatten(AX))+[aX]:
    ax.fill_between([0,2], 
                       ax.get_ylim()[0]*np.ones(2),
                       ax.get_ylim()[1]*np.ones(2),
                       linewidth=0, alpha=0.1)

pt.set_plot(aX, xticks=[-2,0,2,4], xlabel='time (s)',
            ylabel='norm. pupil\n(% baseline)',
            title='N=%i sessions' % np.sum(classical))
pt.annotate(AX[0][0], 'N=%i sessions\n' % np.sum(classical),
            (0.,1.), ha='right')

# %%
unorthodox =\
    [p[0]=='Asahi-unorthodox' for p in DATASET['protocols']]

stim_pics_folder = os.path.expanduser(\
    '~/Documents/Research/2025/Asahi-Design-Alberto/unorthodox')


Nimages = 6
Responses = [[] for i in range(Nimages)]

for f in DATASET['files'][unorthodox]:

    data = physion.analysis.read_NWB.Data(f)
    data.metadata['json_location'] = stim_pics_folder 
    data.init_visual_stim()
    data.build_pupil_diameter()

    if hasattr(data, 'pupil_diameter'):
        Episodes = \
    physion.analysis.episodes.build.EpisodeData(data,
                                                quantities=['pupil_diameter'],
                                                prestim_duration=0.5)

        for i in range(Nimages):
            iCond = Episodes.find_episode_cond(\
                            key='Image-ID', 
                            value=i+1)
            Responses[i].append(\
                Episodes.pupil_diameter[iCond,:].mean(axis=0))


# %%
fig2, aX = pt.figure(ax_scale=(1.2,1.2))
fig, AX = pt.figure((Nimages,2))

Labels = [" -> Grey-Screen", " -> Gradient-Reversed", " -> Asahi", 
          " -> Grey-Screen", " -> Gradient-Reversed", " -> Gradient-Reversed+Patch"]
COLORS = ['tab:grey', 'tab:blue','tab:red', 'tab:grey', 'tab:blue', 'tab:purple']

from scipy import stats
import numpy as np

for i in range(Nimages):
    inset = pt.inset(AX[0][i], [0.1,1.,0.8,0.8])
    iStim = np.flatnonzero(\
        np.array(data.visual_stim.experiment['Image-ID'])==(i+1))[0] 
    pt.matrix(data.visual_stim.get_image(iStim),
              colormap=pt.gray, vmin=0, vmax=1, ax=inset)
    inset.axis('off')
    inset.set_title(Labels[i], fontsize=6, color=COLORS[i])
    pt.annotate(aX, i*'\n'+Labels[i], (1,1), va='top', color=COLORS[i])

    pt.plot(Episodes.t, np.mean(Responses[i], axis=0), 
            sy=stats.sem(Responses[i], axis=0),
            ax=AX[0][i], color=COLORS[i])

    norm_resp = [(resp-np.mean(resp[Episodes.t<0]))/np.mean(resp[Episodes.t<0]) for resp in Responses[i]]

    pt.plot(Episodes.t, 100*np.mean(norm_resp, axis=0), 
            sy=100*stats.sem(norm_resp, axis=0),
            ax=AX[1][i], color=COLORS[i])
    pt.plot(Episodes.t, 100*np.mean(norm_resp, axis=0), 
            sy=100*stats.sem(norm_resp, axis=0),
            color=COLORS[i], ax=aX)

    # pt.set_plot(AX[0][i], xticks=[-2,0,2], xlim=[-2,2],
    pt.set_plot(AX[0][i], xticks=[0,1], xlim=[-0.5,1],
                ylabel='pupil diam.\n(mm)' if i==0 else '')
    # pt.set_plot(AX[1][i], xticks=[-2,0,2], xlim=[-2,2], 
    pt.set_plot(AX[1][i], xticks=[0,1], xlim=[-0.5,1],
                xlabel='time (s)', ylabel='norm. pupil\n(% baseline)' if i==0 else '')

pt.set_common_ylims(AX[0])
pt.set_common_ylims(AX[1])

for ax in list(pt.flatten(AX))+[aX]:
    ax.fill_between([0,2], 
                       ax.get_ylim()[0]*np.ones(2),
                       ax.get_ylim()[1]*np.ones(2),
                       linewidth=0, alpha=0.1)

# pt.set_plot(aX, xticks=[-2,0,2,4], 
pt.set_plot(aX, xticks=[0,1], xlim=[-0.5,1], ylim=[-1.5,1.5],
            xlabel='time (s)', ylabel='norm. pupil\n(% baseline)',
            title='N=%i sessions' % np.sum(unorthodox))
pt.annotate(AX[0][0], 'N=%i sessions\n' % np.sum(unorthodox),
            (0.,1.), ha='right')



# %%
unorthodox =\
    [p[0]=='Asahi-unorthodox-SIZE-vars' for p in DATASET['protocols']]

stim_pics_folder = os.path.expanduser(\
    '~/Documents/Research/2025/Asahi-Design-Alberto/unorthodox-SIZE-vars')


Nimages = 9
Responses = [[] for i in range(Nimages)]

for f in DATASET['files'][unorthodox]:

    data = physion.analysis.read_NWB.Data(f)
    data.metadata['json_location'] = stim_pics_folder 
    data.init_visual_stim()
    data.build_pupil_diameter()

    if hasattr(data, 'pupil_diameter'):
        Episodes = \
    physion.analysis.episodes.build.EpisodeData(data,
                                                quantities=['pupil_diameter'],
                                                prestim_duration=0.5)

        for i in range(Nimages):
            iCond = Episodes.find_episode_cond(\
                            key='Image-ID', 
                            index=i)
                            # value=i+1)
            Responses[i].append(\
                Episodes.pupil_diameter[iCond,:].mean(axis=0))


# %%
fig2, aX = pt.figure(ax_scale=(1.4,1.4))
fig, AX = pt.figure((Nimages,2))

Labels = [
    'Grey-Screen',
    'Medium-Gradient-Reversed',
    'Medium-Asahi-Stimulus',
    'Grey-Screen',
    'Small-Gradient-Reversed',
    'Small-Asahi-Stimulus',
    'Grey-Screen',
    'Gradient-Reversed',
    'Large-Asahi-Stimulus']

COLORS = ['tab:grey', 'tab:blue','tab:red', 
          'tab:grey', 'tab:blue', 'tab:purple',
          'tab:grey', 'tab:blue', 'tab:orange']

from scipy import stats
import numpy as np

for i in range(Nimages):
    inset = pt.inset(AX[0][i], [0.1,1.,0.8,0.8])
    iStim = np.flatnonzero(\
        np.array(data.visual_stim.experiment['Image-ID'])==(i+1))[0] 
    pt.matrix(data.visual_stim.get_image(iStim),
              colormap=pt.gray, vmin=0, vmax=1, ax=inset)
    inset.axis('off')
    inset.set_title(Labels[i], fontsize=6, color=COLORS[i])

    pt.plot(Episodes.t, np.mean(Responses[i], axis=0), 
            sy=stats.sem(Responses[i], axis=0),
            ax=AX[0][i], color=COLORS[i])

    norm_resp = [(resp-np.mean(resp[Episodes.t<0]))/np.mean(resp[Episodes.t<0]) for resp in Responses[i]]

    pt.plot(Episodes.t, 100*np.mean(norm_resp, axis=0), 
            sy=100*stats.sem(norm_resp, axis=0),
            ax=AX[1][i], color=COLORS[i])
    if i%3==2:
        pt.annotate(aX, Labels[i]+i*'\n', (1,0), va='bottom', color=COLORS[i])
        pt.plot(Episodes.t, 100*np.mean(norm_resp, axis=0), 
                sy=100*stats.sem(norm_resp, axis=0),
                color=COLORS[i], ax=aX)

    pt.set_plot(AX[0][i], xticks=[-1,0,1], xlim=[-1,1],
                ylabel='pupil diam.\n(mm)' if i==0 else '')
    pt.set_plot(AX[1][i], xticks=[-1,0,1], xlim=[-1,1], xlabel='time (s)',
                ylabel='norm. pupil\n(% baseline)' if i==0 else '')

pt.set_common_ylims(AX[0])
pt.set_common_ylims(AX[1])

for ax in list(pt.flatten(AX))+[aX]:
    ax.fill_between([0,1], 
                     ax.get_ylim()[0]*np.ones(2),
                     ax.get_ylim()[1]*np.ones(2),
                     linewidth=0, alpha=0.1)

pt.set_plot(aX, xticks=[-1,0,1], xlim=[-1,1], 
            xlabel='time (s)', ylim=[-1,2],
            ylabel='norm. pupil\n(% baseline)',
            title='N=%i sessions' % np.sum(unorthodox))
pt.annotate(AX[0][0], 'N=%i sessions\n' % np.sum(unorthodox),
            (0.,1.), ha='right')

# %%
