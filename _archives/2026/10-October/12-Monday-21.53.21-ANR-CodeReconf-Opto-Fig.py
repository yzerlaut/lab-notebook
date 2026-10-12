# %%
import sys, os
import numpy as np
from scipy.ndimage import gaussian_filter1d

sys.path += ['physion/src']
from physion.analysis.read_NWB import Data, scan_folder_for_NWBfiles
from physion.analysis.episodes.build import EpisodeData
from physion.utils import plot_tools as pt

# %%
folder = os.path.expanduser('~/DATA/Sally/')
dataset = scan_folder_for_NWBfiles(folder,
                                   for_protocol='1sPrePost')

# %%
data = Data(dataset['files'][0])
# %%
data.build_MUA()
data.build_spikes()
data.build_opto()

# %%
ep = EpisodeData(data, quantities=['MUA', 'spikes', 'opto'])
# %%

stim_cond = ep.contrast<1.
opto_cond = ep.opto.mean(axis=-1)>0

fig, ax = pt.figure()

smoothing = 15
ax.plot(ep.t, 
        gaussian_filter1d(ep.MUA[stim_cond & opto_cond,:].mean(axis=(0,1)), smoothing),
        color='tab:blue')
ax.plot(ep.t, 
        gaussian_filter1d(ep.MUA[stim_cond & ~opto_cond,:].mean(axis=(0,1)), smoothing),
        color='tab:grey')
ax.axis('off')
pt.draw_bar_scales(ax, Xbar=1, Xbar_label='1s', Ybar=10, Ybar_label='10$\mu$V')

# %%

stim_cond = (ep.contrast<0.5) # & (ep.angle==90)
opto_cond = ep.opto.mean(axis=-1)>0

fig, ax = pt.figure()

smoothing = 15
ax.plot(ep.t, 
        gaussian_filter1d(ep.spikes[stim_cond & opto_cond,:].mean(axis=(0,1)), smoothing),
        color='tab:blue')
ax.plot(ep.t, 
        gaussian_filter1d(ep.spikes[stim_cond & ~opto_cond,:].mean(axis=(0,1)), smoothing),
        color='tab:grey')
ax.axis('off')
# pt.draw_bar_scales(ax, Xbar=1, Xbar_label='1s', Ybar=10, Ybar_label='10$\mu$V')

# %%
stim_cond = (ep.contrast>0.5) # & (ep.angle==90)
opto_cond = ep.opto.mean(axis=-1)>0

smoothing = 50
for unit in range(ep.spikes.shape[1]):
    fig, ax = pt.figure()
    ax.plot(ep.t, 
            gaussian_filter1d(ep.spikes[stim_cond & opto_cond, unit, :].mean(axis=0), smoothing),
            color='tab:blue')
    ax.plot(ep.t, 
            gaussian_filter1d(ep.spikes[stim_cond & ~opto_cond, unit, :].mean(axis=0), smoothing),
            color='tab:grey')
    ax.axis('off')
    ax.set_title('unit #%i' % unit)
# pt.draw_bar_scales(ax, Xbar=1, Xbar_label='1s', Ybar=10, Ybar_label='10$\mu$V')
# %%
stim_cond = (ep.contrast>0.5) # & (ep.angle==90)
smoothing = 30
units = [113, 103, 95, 88, 45, 41, 25, 115, 109, 88, 90, 80, 59, 38]
fig, AX = pt.figure(axes=(10, 13))
# for unit, ax in zip(units, pt.flatten(AX)):
for unit, ax in zip(range(ep.spikes.shape[1]), pt.flatten(AX)):

    for stim_cond, color in zip(
        [(ep.contrast==0.4) & ~opto_cond, (ep.contrast==1.0) & opto_cond][::-1],
        ['tab:grey', 'tab:blue'][::-1]):
        ax.fill_between(ep.t, 0*ep.t,
                gaussian_filter1d(ep.spikes[stim_cond, unit, :].mean(axis=0), smoothing),
                color=color)
    ylim = ax.get_ylim()
    ax.fill_between([0,2], ylim[0]*np.ones(2), ylim[1]*np.ones(2), color='k', alpha=.1, lw=0)
    ax.fill_between([-1,3], -0.05*ylim[1]*np.ones(2), -0.15*ylim[1]*np.ones(2), color='tab:blue', alpha=.5, lw=0)
    ax.plot([-1,2], ylim[0]*np.ones(2), ylim[1]*np.ones(2), color='k', alpha=.1, lw=0)
    ax.axis('off')
    ax.set_title('unit #%i' % unit)
    pt.draw_bar_scales(ax, Xbar=1, Xbar_label='1s', Ybar=1e-3, Ybar_label='1Hz')

# %%
