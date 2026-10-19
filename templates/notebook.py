# %%
import sys, os
sys.path += ['../physion/src']
from physion.analysis.read_NWB import Data, scan_folder_for_NWBfiles

folder = os.path.expanduser('~/DATA/physion_Demo-Datasets/SST-WT')
dataset = scan_folder_for_NWBfiles(folder)
# filenames = [\
#     '2023_02_15-13-30-47',
#     '2023_02_15-14-05-01',
#     '2023_02_15-15-10-04',
#     '2024_08_27-10-52-11',
#     '2024_08_27-11-16-53',
#     ]
# dataset = scan_folder_for_NWBfiles(folder, from_filenames=filenames)

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
