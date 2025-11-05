# %%
import sys, os, json
import numpy as np
sys.path += ['./physion/src']
import physion
from physion.utils import plot_tools as pt

# %%
with open(\
     'physion/src/physion/acquisition/protocols/demo/3-screens.json',
     'r') as f:
    protocol = json.load(f)
stim = physion.visual_stim.build.build_stim(protocol)
    
# %%
img = stim.get_image(2)
pt.matrix(img)
# %%
img2 = stim.restrict_to_screen(img, 1)
pt.matrix(img2)
# %%
np.unique(img2)

# %%
