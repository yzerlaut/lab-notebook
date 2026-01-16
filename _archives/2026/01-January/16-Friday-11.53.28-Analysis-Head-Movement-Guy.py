# %%
import os, sys
import mat73 # pip install mat73
from scipy import io
import numpy as np

sys.path += ['./physion/src']
from physion.electrophy.LFP.NSI import my_cwt
import physion.utils.plot_tools as pt
pt.set_style('dark')
import numpy as np
from physion.electrophy.LFP.NSI import my_cwt

# %%
folder = os.path.expanduser('~/Downloads/Collaboration_Yann_BrainState')

# 1)
# t = mat73.loadmat(os.path.join(folder, 'animal18_a74d1s1_time.mat'))['data']*dt
# 2)
# TableAngle= mat73.loadmat(os.path.join(folder, 'animal18_a74d1s1_ADC00.mat'))['data']
# 3)
ledOnTrials = io.loadmat(os.path.join(folder, 'animal18_a74d1s1ledOnTrials.mat'))

# %%

class Data:
    def __init__(self, 
                 filename=None,
                #  channel=20,
                 ):

        dt = 1./30e3 # 30kHz sampling
        dt = 1./1250. # subsampled LFP

        ledOnTrials = io.loadmat(\
            os.path.join(folder, 'animal18_a74d1s1ledOnTrials.mat'))
        
        self.LED=\
              2*ledOnTrials['ledon'][0]+ledOnTrials['ledoff'][0]-1 # ON=1, OFF=0
        self.LED = self.LED[:78]
        # WHY ?? LED has 162 episodes and the LFP only half episodes ???

        self.nTrials = len(self.LED)
        # 4)
        LFP = mat73.loadmat(os.path.join(folder, 'animal18_a74d1s1_bothDirLFP_data.mat'))

        # LFP from 2 probes: shape (nChannels, nTrials, time)
        self.LFP = [\
            np.array(LFP['LFPbyChan']['LFPbyChan_vo'])[2:-2:4,:,:],
            np.array(LFP['LFPbyChan']['LFPbyChan_vs'])[2:-2:4,:,:]]

        self.nChannels = self.LFP[0].shape[0]

        # Head Rotation: shape (nTrials, time)
        self.headRot = np.array(LFP['dirWave']) 
        # build sign from it
        self.headRotSign = np.zeros(self.nTrials)
        for ep in range(self.nTrials):
            if np.max(self.headRot[ep,:])>50:
                self.headRotSign = +1
            elif np.min(self.headRot[ep,:])<-50:
                self.headRotSign = -1

        # time array
        self.t = np.arange(self.LFP[0].shape[2])*dt
        self.dt = dt

        # time-frequency analysis
        self.freqs = np.linspace(2, 140, 40)

        # merging channels
        self.time_freq_power = np.zeros((self.nTrials, 
                                         len(self.freqs),
                                         len(self.t)))
        for ep in range(self.nTrials):
            for chan in range(self.nChannels):
                self.time_freq_power[ep, :, :] +=\
                    np.abs(my_cwt(self.LFP[0][chan, ep, :], 
                                  self.freqs, self.dt))

data = Data()

# %%

def norm(x):
    return (x-x.min())/(x.max()-x.min())

def show_single_trial(data, ep, 
                      probe=1, chan=7):
    
    fig, AX = pt.figure(axes_extents=[[[1,2]],[[1,3]],[[1,2]]],
                        ax_scale=(1.3,.2))

    AX[0].plot(data.t, data.LFP[probe-1][chan, ep, :], lw=0.1,)
    AX[0].axis('off')
    pt.draw_bar_scales(AX[0], Xbar=1, Xbar_label='1s', 
                       Ybar=500, Ybar_label='500$\mu$V')
    
    c = AX[1].contourf(data.t, data.freqs, data.time_freq_power[ep,:,:], cmap=pt.binary)
    pt.set_plot(AX[1], ['left'], ylabel='freq. (Hz)', yscale='log')

    AX[2].plot(data.t, norm(data.headRot[ep,:]))
    if data.LED[ep]:
        AX[2].fill_between([0,1,1,5,5,6],[0,0,0,0,0,0], [0,0,1,1,0,0], alpha=.2, lw=0)
    AX[2].axis('off')

    pt.annotate(AX[0], 'trial #%i' % (ep+1), (1,1), va='top', ha='right')

for i in range(3, 5):
    show_single_trial(data, i)

# %%

cond = (data.LED==0)

fig, ax = pt.figure()
c = ax.contourf(data.t, data.freqs, 
                data.time_freq_power[cond,:,:].mean(axis=0), 
                cmap=pt.binary)
pt.set_plot(ax, ['left'], ylabel='freq. (Hz)', yscale='log')


# %%
def wavelet_power(data, ep, chan):
    return np.abs(my_cwt(data[chan, ep, :], data.freqs, data.dt)

# data.mean_power = np.mean(\
#     for chan in range(data.nChannels))

def compute_mean_time_freq_power(data):
    data.wvlt_power = np.zeros((nTrials, 
    for c in range(data.LFP1.shape[0]):
        data.
# freqs = np.logspace(0, 2, 20)

    physion.electrophy.LFP.compute_pLFP()
compute_wavelet(data)

def compute_pLFP(data):
    pass

# %%

trials = {
    'on-right':[],
    'on-left':[],
    'off-right':[],
    'off-left':[],
}

for ep in range(78):

    if data.LED[ep]==1:
        trial = 'on-'
    else:
        trial = 'off-'

    if np.max(data.headRot[ep])>50:
        trial += 'right'
    elif np.min(data.headRot[ep])<-50:
        trial += 'left'
    else:
        print(data.LED[ep], np.min(data.headRot[ep]))

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
            AX[c][i].plot(t, data.LFP1[c, ep, :], color=pt.autumn(c/4.), lw=0.1)

        AX[3][i].plot(t, data.headRot[ep], 'k-')

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
import sys
sys.path += ['physion/src']
import physion.utils.plot_tools as pt

# %%
pt.time_freq
# %%
trials
# %%
import sys
sys.path += ['./physion/src']
from physion.electrophy.LFP.NSI import my_cwt
import physion.utils.plot_tools as pt
import numpy as np

dt, tstop = 1e-4, 1.
t = np.arange(int(tstop/dt))*dt

freq1, width1, freq2, width2, freq3, width3 = 10., 100e-3, 40., 40e-3, 70., 20e-3
data = 3.2+np.cos(2*np.pi*freq1*t)*np.exp(-(t-.5)**2/2./width1**2)+\
    np.cos(2*np.pi*freq2*t)*np.exp(-(t-.2)**2/2./width2**2)+\
    np.cos(2*np.pi*freq3*t)*np.exp(-(t-.8)**2/2./width3**2)

# Continuous Wavelet Transform analysis
freqs = np.linspace(1, 90, 40)
# freqs = np.logspace(0, 2, 20)
coefs = my_cwt(data, freqs, dt)

# fig, ax = time_freq(t, freqs, coefs)    
fig, AX = pt.time_freq_signal(t, freqs, data, coefs, freq_scale='lin')    
# %%
fig, ax = pt.figure(ax_scale=(1.4,1.4))
c = ax.contourf(t, freqs, np.abs(coefs), cmap=pt.binary)
pt.set_plot(ax, ['left'], ylabel='freq. (Hz)', yscale='log')
pt.draw_bar_scales(ax, Xbar=.1, Xbar_label='.1s', Ybar=1e-12, color='k')

# %%
