# %%
import sys, os
sys.path += ['physion/src']
from physion.analysis.read_NWB import Data, scan_folder_for_NWBfiles

folder = os.path.expanduser('~/DATA/physion_Demo-Datasets/Neuropix-WT/')
dataset = scan_folder_for_NWBfiles(folder)

# %%
data = Data(dataset['files'][0])
# %%
data.build_firing()
# %%
from physion.analysis.episodes.build import EpisodeData
ep = EpisodeData(data, quantities=['firing'])
# %%
from physion.utils import plot_tools as pt
pt.plot(ep.t, ep.firing.mean(axis=(0,1)))
# %%
