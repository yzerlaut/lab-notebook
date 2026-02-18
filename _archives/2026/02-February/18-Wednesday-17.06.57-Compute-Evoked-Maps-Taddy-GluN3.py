# %%
import pandas as pd

# xlsx = pd.ExcelFile(\
#     os.path.expanduser('~/DATA/Taddy/ODI-GluN3A/DataTable.xlsx'))
# sheet = xlsx.parse(0)

raw_data_path = \
    os.path.expanduser('/Volumes/COMMON/Group-2-ODI/')
    # os.path.expanduser('/Volumes/YANN/ODI-GluN3A/')
    # os.path.expanduser('/Volumes/T7 Touch/ODI')
csv = pd.read_csv(\
    os.path.expanduser('~/DATA/Taddy/ODI-GluN3A/DataTable.csv'),
                    delimiter=';')
NB_path = os.path.expanduser('~/Documents/Notebook/Projects/Taddy-GluN3/figs')

# %%
import sys
sys.path += ['physion/src']
import numpy as np
import physion.utils.plot_tools as pt
from scipy.ndimage import gaussian_filter

def load_Camera_data(imgfolder, t0=0):

    file_list = [f for f in os.listdir(imgfolder) if f.endswith('.npy')]
    _times = np.array([float(f.replace('.npy', '')) for f in file_list])
    _isorted = np.argsort(_times)
    times = _times[_isorted]-t0
    FILES = np.array(file_list)[_isorted]
    nframes = len(times)
    Lx, Ly = np.load(os.path.join(imgfolder, FILES[0])).shape
    if True:
        print('Sampling frequency: %.1f Hz  (datafile: %s)' % (1./np.diff(times).mean(), imgfolder))
        
    return times, FILES, nframes, Lx, Ly


def compute_resp(datafolder,
                 smoothing=(0,3,3),
                 spatial_subsampling=3):

    # load visual stim
    visual_stim = np.load(os.path.join(datafolder, 'visual-stim.npy'),
                          allow_pickle=True).item()
    
    NIdaq_tStart = np.load(os.path.join(datafolder, 'NIdaq.start.npy'),
                          allow_pickle=True).item()
    
    # load
    times, FILES, nframes, Lx, Ly = load_Camera_data(\
                                os.path.join(datafolder, 'ImagingCamera-imgs'),
                                t0=NIdaq_tStart)
    
    dt = 0.05 # seconds
    tstart, tstop = -3, 7

    nt = int((tstop-tstart)/dt)
    t = tstart+np.arange(nt)*dt

    Response = np.zeros((nt, Lx, Ly))
    Ns = np.zeros(nt) # count images per time step

    for tS in visual_stim['time_start']:
        new_time = times-tS
        cond = (new_time>(tstart-dt)) & (new_time<(tstop+dt))
        for ts, file in zip(new_time[cond], FILES[cond]):
            i0 = np.argmin((t-ts)**2)
            img = np.load(os.path.join(datafolder, 'ImagingCamera-imgs', file))
            Response[i0,:,:] += img
            Ns[i0] +=1
    for i in range(nt):
        Response[i,:,:] /= Ns[i0]
    
    # removing bad sampling at boundaries
    return t[1:-1],\
         gaussian_filter(Response[1:-1,:,:], smoothing)
