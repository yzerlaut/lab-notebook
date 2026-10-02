# %%
import sys, os
sys.path += ['physion/src']
from physion.analysis.read_NWB import Data
from physion.analysis.episodes.build import EpisodeData
from physion.utils import plot_tools as pt
folder = os.path.expanduser('~/DATA/Sally/Npx_WT_prelim_2026/NWBs')
data = Data(os.path.join(folder, '2026_08_26-16-22-21.nwb'))

# %%
# before restriction
data.build_firing()
print(data.firing.shape)
ep = EpisodeData(data, quantities=['firing'], protocol_id=0)
ep.firing += 0.01

fig, ax = pt.figure()
ax.imshow(ep.firing.mean(axis=0),
            cmap=pt.binary,
            interpolation='none',
            origin='lower',
            aspect='auto')
pt.set_plot(ax, title='all channels')

# %%
data.restrict_to_region('VISp')
print(data.firing.shape)
ep = EpisodeData(data, quantities=['firing'], protocol_id=0)
ep.firing += 0.01

fig, ax = pt.figure()
ax.imshow(ep.firing.mean(axis=0),
            cmap=pt.binary,
            interpolation='none',
            # vmin=0, vmax=2, 
            extent = (ep.t[0], ep.t[-1],
                    0, ep.firing.shape[0]),
            origin='lower',
            aspect='auto')
pt.set_plot(ax, title='restricted to V1')

# %%
