# %%
from allensdk.core.brain_observatory_cache import BrainObservatoryCache
import matplotlib.pylab as plt
from PIL import Image

# %%
boc = BrainObservatoryCache(manifest_file='boc/manifest.json')
# %%
data_set = boc.get_ophys_experiment_data(501498760)


# read in the array of images
scenes = data_set.get_stimulus_template('natural_scenes')

scene_nums = range(10)

# display a couple of the scenes
for scene in range(len(scenes)):
    # fig, ax = plt.subplots(1)
    # ax.imshow(scenes[scene,:,:], cmap='gray')
    # ax.set_axis_off()
    # ax.set_title('scene %d' % scene)
    im = Image.fromarray(scenes[scene,:,:])
    im = im.convert('RGB')
    im.save("Natural-Images-Allen/%i.jpeg" % (scene+1))
