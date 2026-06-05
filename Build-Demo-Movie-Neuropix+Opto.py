# %%
import os, sys
import numpy as np
import matplotlib.pylab as plt
sys.path += ['physion/src']
from physion.assembling.dataset import read_spreadsheet
from physion.utils import plot_tools as pt
from physion.dataviz import snapshot

from open_ephys.analysis import Session as OpenEphysSession

# %%
datafolder = os.path.expanduser('~/DATA/2026_04_24').replace('/', os.path.sep)
iRec = 1 

datatable, _, _ = read_spreadsheet(\
                    os.path.join(datafolder, 'DataTable.xlsx'),
                            get_metadata_from='files')

# %%
# example data from physion_Demo-Datasets:
nwbfile = os.path.expanduser(\
    '~/DATA/2026_04_24/%s-%s.nwb' % (datatable['day'][iRec], datatable['time'][iRec]))
raw_data_folder =os.path.join(datafolder, datatable['time'][iRec])


# %% [markdown]
# ##  Load NWB data and build data modalities

# %%
from physion.analysis.read_NWB import Data
data = Data(nwbfile)
data.init_visual_stim()#force_degree=True)
# data.init_visual_stim(force_degree=True)

# data.build_dFoF()
data.build_running_speed()

# add some smoothing for display
from scipy.ndimage import gaussian_filter1d

data.build_facemotion()
data.facemotion = gaussian_filter1d(data.facemotion, 2)
data.build_pupil_diameter()
# data.pupil_diameter = gaussian_filter1d(data.pupil_diameter, 8)


# %%
if False:
    from physion.dataviz.raw import plot as plot_raw, find_default_plot_settings
    settings = find_default_plot_settings(data)#, with_subsampling=True)
    _ = plot_raw(data, settings=settings, tlim=[100, 250])

# %%
if False:
    settings = find_default_plot_settings(data, with_subsampling=True)
    _ = plot_raw(data, settings=settings, tlim=[0, 900])

# %% [markdown]
# ##  Load FaceCamera data

# %%
from physion.utils.camera import CameraData
faceCamera = CameraData('FaceCamera', raw_data_folder)

# %%
rigCamera = CameraData('RigCamera', raw_data_folder)

# %% # load EPHYS data
nStart, nStop = datatable['nStart'][iRec], datatable['nStop'][iRec]

# load the open-ephys data:
session = OpenEphysSession(\
            os.path.join(datafolder, datatable['Npx-Folder'][iRec]))

node = int(datatable['Npx-Rec'][iRec].split('node')[1].split('/')[0])
rec_id = int(datatable['Npx-Rec'][iRec].split('rec')[1])-1
rec = session.recordnodes[node].recordings[rec_id]
rec.t = np.linspace(0, data.tlim[1], nStop-nStart)

# %%
params =\
{
    " ############################################## ":"",
    " ############  data sample properties ######### ":"",
    " ############################################## ":"",
    "tlim":[132,240],
    "zoomROIs":[0,1],
    "                                                ":"",
    " ############################################## ":"",
    " #############  ephys properties ############ ":"",
    " ############################################## ":"",
    "ephys_interval":15.,
    "ephys_channels":[92, 91, 50, 81, 71, 105],
    "ephys_shift_factor":4,
    "ephys_Tbar":0.5,
    "                                                ":"",
    " ############################################## ":"",
    " ##########  Face-camera properties ########### ":"",
    " ############################################## ":"",
    "Face_Lim":[0, 0, 10000, 10000],
    "Face_clip":[0.3,1.0],
    "Face_NL":4,
    "                                                ":"",
    " ############################################## ":"",
    " ##########  Rig-camera properties ############ ":"",
    " ############################################## ":"",
    "Rig_Lim":[0, 0, 10000, 10000],
    "Rig_NL":2,
    "                                                ":"",
    " ############################################## ":"",
    " ##########  annotation properties ############ ":"",
    " ############################################## ":"",
    "Tbar":5, 
    "Tbar_loc":1.0,
    "with_screen_inset":False,
    "                                                ":"",
    " ############################################## ":"",
    " ##########   layout properties  ############## ":"",
    " ############################################## ":"",
    "fractions": {"running":0.3, "running_start":0.1,
                  "whisking":0.25, "whisking_start":0.35,
                  "LED":0.1, "LED_start":0.,
                  "pupil":0.45, "pupil_start":0.5,
                  "rois":0.4, "rois_start":0.29,
                  "visual_stim":2, "visual_stim_start":2.0},
    "                                                ":""
}
params['ephys_nStart'], params['ephys_nStop'] = nStart, nStop
# %%

def show(time):
    fig, AX = snapshot.layout(imaging=False)

    # snapshot.init_imaging(AX, params, data)
    snapshot.plot_traces(AX, params, data)
    snapshot.init_screen(AX, data)
    snapshot.update_screen(AX, data, time)
    snapshot.init_camera(AX, params, faceCamera, 'Face')
    snapshot.init_camera(AX, params, rigCamera, 'Rig')
    snapshot.update_camera(AX, params, faceCamera, time, 'Face')
    snapshot.update_camera(AX, params, rigCamera, time, 'Rig')
    snapshot.init_pupil(AX, data, params, faceCamera)
    snapshot.update_pupil(AX, data, params, faceCamera, time)
    snapshot.init_whisking(AX, data, params, faceCamera)
    snapshot.update_whisking(AX, data, params, faceCamera, time)
    snapshot.update_timer(AX, time)
    snapshot.init_ephys(AX, data, params, rec, time)
    snapshot.update_ephys(AX, data, params, rec, time)

    return fig, AX

# for time in 130+np.arange(3)*16:
#     show(time)
# pt.plt.show()


# %% [markdown]
# ## Build the movie
# %%
if False:
    from physion.dataviz import movie
    fig, AX = snapshot.layout(imaging=False)
    _, _, ani = movie.build(fig, AX, data, params,
                            faceCamera=faceCamera,
                            rigCamera=rigCamera,
                            ephysData=rec,
                            Ndiscret=50)
    pt.plt.show()
    # movie.write(ani, FPS=5)

# %%
import matplotlib.animation as animation

Ndiscret=400
times = np.linspace(params['tlim'][0], params['tlim'][1], 
                    Ndiscret)
if True:
    for i, t in enumerate(times):
        fig, AX = show(t)
        fig.savefig('tmp/%i.jpg' % i, dpi=150)
        pt.plt.close(fig)

# %%
from PIL import Image
def build():

    fig, ax = plt.subplots(1, figsize=(8,4.5))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    im0 = Image.open('tmp/0.jpg')
    im = ax.imshow(im0)
    ax.axis('off')

    def update(i=0):

        im0 = Image.open('tmp/%i.jpg' % i)
        im.set_array(im0)

        return [im]

    ani = animation.FuncAnimation(fig, 
                                  update,
                                  np.arange(len(times)),
                                  init_func=update,
                                  interval=100,
                                  blit=True)

    return fig, ax, ani

from physion.dataviz import movie
_, _, ani = build()
movie.write(ani, FPS=10, DPI=150)
