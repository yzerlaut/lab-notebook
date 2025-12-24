# %%
# import sys
# sys.path += ['./']
import plot_tools as pt
import os
import mat73 # pip install mat73
from scipy import io
import numpy as np

# %%
folder = os.path.expanduser('~/Downloads/Collaboration_Yann_BrainState')

dt = 1./30e3 # 30kHz sampling

dt = 1./1250. # subsampled LFP

# 1)
# t = mat73.loadmat(os.path.join(folder, 'animal18_a74d1s1_time.mat'))['data']*dt
# 2)
# TableAngle= mat73.loadmat(os.path.join(folder, 'animal18_a74d1s1_ADC00.mat'))['data']
# 3)
ledOnTrials = io.loadmat(os.path.join(folder, 'animal18_a74d1s1ledOnTrials.mat'))
LEDtrials = 2*ledOnTrials['ledon'][0]+ledOnTrials['ledoff'][0]-1 # ON=1, OFF=0
# 4)
LFP = mat73.loadmat(os.path.join(folder, 'animal18_a74d1s1_bothDirLFP_data.mat'))
LFPprobe1 = LFP['LFPbyChan']['LFPbyChan_vo']
LFPprobe2 = LFP['LFPbyChan']['LFPbyChan_vs']
t = np.arange(len(LFPprobe1[0][0]))*dt
# %%

trials = {
    'on-right':[],
    'on-left':[],
    'off-right':[],
    'off-left':[],
}

for ep in range(78):

    if LEDtrials[ep]==1:
        trial = 'on-'
    else:
        trial = 'off-'

    if np.max(LFP['dirWave'][ep])>50:
        trial += 'right'
    elif np.min(LFP['dirWave'][ep])<-50:
        trial += 'left'
    else:
        print(LEDtrials[ep], np.min(LFP['dirWave'][ep]))

    trials[trial].append(ep)

# %%
fig, AX = pt.figure(hspace=0.2, wspace=0.5, 
                    ax_scale=(1,1.2),
                    axes=(4,5))


chans = [10,30,50]

for i, trial in enumerate(trials):
    AX[0][i].set_title(trial+'\n(n=%i trials)' % len(trials[trial]))

    ep = [0]
    for ep in trials[trial][:4]:
        for c, ch in enumerate(chans):
            AX[c][i].plot(t, LFPprobe1[c][ep], color=pt.autumn(c/4.), lw=0.1)

        AX[3][i].plot(t, LFP['dirWave'][ep], 'k-')

        if 'on-' in trial:
            AX[4][i].plot([0,1,1,5,5,6], [0,0,1,1,0,0], 'k-')
        else:
            AX[4][i].plot([0,6], [0,0], 'k-')

    AX[4][i].set_ylim([-1,2])
    AX[3][i].set_ylim([-70,+70])

    pt.draw_bar_scales(AX[4][i], Xbar=1, Xbar_label='1s', Ybar=1e-3)

for c, ch in enumerate(chans):
    pt.annotate(AX[c][0], 'chan. #%i' % ch, (0.,0.5), 
            ha='right', va='center', rotation=90, color=pt.autumn(c/4.))
    pt.draw_bar_scales(AX[c][1], Xbar=1e-6,
                Ybar=200, Ybar_label='200$\mu$V')
pt.annotate(AX[3][0], 'rotation', (0.,0.5), 
        ha='right', va='center', rotation=90)
pt.annotate(AX[4][0], 'LED', (0.,0.5), 
        ha='right', va='center', rotation=90)

for ax in pt.flatten(AX):
    ax.axis('off')
pt.set_common_xlims(AX)
# %%
# %%