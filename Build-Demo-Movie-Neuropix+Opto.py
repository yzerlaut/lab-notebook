# %%
import os, sys
import numpy as np
sys.path += ['physion/src']
import physion

from open_ephys.analysis import Session as OpenEphysSession

# %%
datafolder = os.path.expanduser('~/DATA/2026_04_24').replace('/', os.path.sep)
iRec = 1 

datatable, _, _ = physion.assembling.dataset.read_spreadsheet(\
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
data = physion.analysis.read_NWB.Data(nwbfile)
data.init_visual_stim()#force_degree=True)
# data.init_visual_stim(force_degree=True)

# data.build_dFoF()
data.build_running_speed()

# add some smoothing for display
from scipy.ndimage import gaussian_filter1d

data.build_facemotion()
data.facemotion = gaussian_filter1d(data.facemotion, 2)
data.build_pupil_diameter()
data.pupil_diameter = gaussian_filter1d(data.pupil_diameter, 8)

# %%
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
NIdaq_Tstart = np.load(os.path.join(raw_data_folder, 'NIdaq.start.npy'))[0]
faceCamera = physion.utils.camera.CameraData(\
                        'FaceCamera', raw_data_folder,
                        t0=NIdaq_Tstart)


# %%
rigCamera = physion.utils.camera.CameraData(\
                        'RigCamera', raw_data_folder,
                        t0=NIdaq_Tstart)
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
    "tlim":[100,250],
    "zoomROIs":[0,1],
    "                                                ":"",
    " ############################################## ":"",
    " #############  ephys properties ############ ":"",
    " ############################################## ":"",
    "ephys_interval":1.,
    "ephys_channels":[50, 69, 81, 119],
    "ephys_shift_factor":4,
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
# %%
time = 0
import matplotlib.pylab as plt
def update_ephys(AX, data, params, rec, t):

    i0 = np.argmin((rec.t-t)**2)
    
    cond = (rec.t>(t-params['ephys_interval']/2.)) & (rec.t<(t+params['ephys_interval']/2.))

    means = [rec.continuous['ProbeA'].samples[nStart:nStop,chan][cond].mean() for chan in params['ephys_channels']]
    stds = [rec.continuous['ProbeA'].samples[nStart:nStop,chan][cond].std() for chan in params['ephys_channels']]

    for c, chan in enumerate(params['ephys_channels']):
        y = (rec.continuous['ProbeA'].samples[nStart:nStop,chan][cond]-means[c])/stds[c]
        AX['axEphys'].plot(rec.t[cond]-t, y+params['ephys_shift_factor']*c, lw=0.5, color=plt.cm.Dark2(c))

    AX['axEphys'].plot([0,0.1], [0,0])
for time in [100, 151.2]:

    fig, AX = physion.dataviz.snapshot.layout(imaging=False)

    # physion.dataviz.snapshot.init_imaging(AX, params, data)
    physion.dataviz.snapshot.plot_traces(AX, params, data)
    physion.dataviz.snapshot.init_screen(AX, data)
    physion.dataviz.snapshot.update_screen(AX, data, time)
    physion.dataviz.snapshot.init_camera(AX, params, faceCamera, 'Face')
    physion.dataviz.snapshot.init_camera(AX, params, rigCamera, 'Rig')
    physion.dataviz.snapshot.update_camera(AX, params, faceCamera, time, 'Face')
    physion.dataviz.snapshot.update_camera(AX, params, rigCamera, time, 'Rig')
    physion.dataviz.snapshot.init_pupil(AX, data, params, faceCamera)
    physion.dataviz.snapshot.update_pupil(AX, data, params, faceCamera, time)
    physion.dataviz.snapshot.init_whisking(AX, data, params, faceCamera)
    physion.dataviz.snapshot.update_whisking(AX, data, params, faceCamera, time)
    physion.dataviz.snapshot.update_timer(AX, time)
    update_ephys(AX, data, params, rec, time)
    physion.utils.plot_tools.plt.show()

    


# %% [markdown]
# ## Build the movie

# %%
if False:
    fig, AX = physion.dataviz.snapshot.layout(imaging=False)
    _, _, ani = physion.dataviz.movie.build(fig, AX, data, params,
                                            faceCamera=faceCamera,
                                            rigCamera=rigCamera,
                                            ephysData=rec,
                                            Ndiscret=200)
    physion.dataviz.movie.write(ani, FPS=5)