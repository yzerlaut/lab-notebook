# %%
import pandas as pd

# xlsx = pd.ExcelFile(\
#     os.path.expanduser('~/DATA/Taddy/ODI-GluN3A/DataTable.xlsx'))
# sheet = xlsx.parse(0)

raw_data_path = \
    os.path.expanduser('/Volumes/T7 Touch/ODI')
csv = pd.read_csv(os.path.join(raw_data_path, 'DataTable.csv'),
                    delimiter=';')

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
                 smoothing=(2,2,2)):

    # load visual stim
    visual_stim = np.load(os.path.join(datafolder, 'visual-stim.npy'),
                          allow_pickle=True).item()
    
    NIdaq_tStart = np.load(os.path.join(datafolder, 'NIdaq.start.npy'),
                          allow_pickle=True).item()
    
    # load
    times, FILES, nframes, Lx, Ly = load_Camera_data(\
                                os.path.join(datafolder, 'ImagingCamera-imgs'),
                                t0=NIdaq_tStart)
    
    dt = 0.1 # seconds
    tstart, tstop = -2, 5

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

# %%
smoothing = (2,2,2)
for k, v, _ in os.walk(raw_data_path):
    if 'ImagingCamera-imgs' in v:
        folder = k
    try:
        t, Resp = compute_resp(folder, smoothing=smoothing)
        np.save(os.path.join(folder, 'resp-maps.npy'),
                {'t': t, 'resp':Resp, 'smoothing':smoothing})
        print('[ok] %s successfully saved'  % folder)
    except BaseException as be:
        print(be)
        print('[XX] pb with: %s '  % folder)

# %% [markdown]

## to transfer files
"""
```
rsync -avhP --exclude "._*" --exclude "Imaging*" --exclude "NIdaq.*" --exclude "*Prelim*" /Volumes/T7\ Touch/ODI/* ~/DATA/Taddy/ODI-GluN3A
```
"""

# %%

def load_mouse(index):

    data = {'id':csv['Subject'][index]}
    for key in ['Pre-Ipsi', 'Pre-Contra', 'Pre-Blank', 
                'Post-Ipsi', 'Post-Contra', 'Post-Blank']:
        folder = os.path.expanduser('~/DATA/Taddy/ODI-GluN3A'+\
                              csv[key][index].replace('~',''))
        resp = np.load(os.path.join(folder, 'resp-maps.npy'),
                    allow_pickle=True).item()
        data[key] = resp['resp']

    data['t'] = resp['t']

    return data

indices = np.arange(len(csv['Groups']))[\
    (csv['Groups']=='Group1') & (csv['Full 3 days MD']=='Yes')]

DATA = []
for i in indices:
    DATA.append(load_mouse(i))


# %%
from scipy.ndimage import gaussian_filter
F0_percentile = 30

def compute_mean_map(t, Resp,
                     response_window = [0.5,1],
                     smoothing=2):

    F0 = np.percentile(Resp[t<0,:,:], F0_percentile, axis=0)
    #
    cond = (t>response_window[0]) & (t<response_window[1])
    return gaussian_filter(\
        (Resp[cond, :,:].mean(axis=0)-F0)/F0,
        smoothing)


def build_OD_maps(maps,
                  threshOD=0.8):

    thresh = threshOD*np.max(maps['ipsi_map'])
    threshCond = maps['ipsi_map']>thresh

    maps['ipsi_map-thresh'] = -np.ones(\
            maps['ipsi_map'].shape)*np.nan
    maps['ipsi_map-thresh'][threshCond] = \
            maps['ipsi_map'][threshCond]
    maps['contra_map-thresh'] = -np.ones(\
            maps['contra_map'].shape)*np.nan
    maps['contra_map-thresh'][threshCond] = \
            maps['contra_map'][threshCond]


    # ----------------------------------- #
    #           ocular dominance          #
    # ----------------------------------- #
    maps['ocular-dominance'] = -np.ones(\
            maps['contra_map'].shape)*np.nan
    maps['ocular-dominance'][threshCond] = \
            (maps['contra_map'][threshCond]-\
                    maps['ipsi_map'][threshCond])/\
            (maps['contra_map'][threshCond]+\
                    maps['ipsi_map'][threshCond])
    
def trace_resp(d, ax, 
               key='Pre-',
               W=6):

    for key, color in zip(\
        ['%s-Ipsi' % key, '%s-Contra' % key, '%s-Blank' % key],
        ['tab:red', 'tab:blue', 'tab:grey']):

        map = d[key+'_map']
        Resp = d[key]
        t = d['t']

        i0, i1 = np.unravel_index(np.argmax(map), np.array(map).shape)

        resp = Resp[:,i0-W:i0+W,i1-W:i1+W].mean(axis=(1,2))
        F0 = np.percentile(resp[1:][t[1:]<0], F0_percentile)
        resp = (resp-F0)/F0
        ax.plot(t[1:-1], resp[1:-1], color=color)

        # resp = Resp[:,:,:].mean(axis=(1,2))
        # F0 = np.percentile(resp[1:][t[1:]<0], F0_percentile)
        # resp = (resp-F0)/F0
        # ax.plot(t[1:-1], resp[1:-1], color='tab:blue')


def plot_mouse(d, 
                 bounds = [0, 0.2], # ADJUST BOUNDS IF NEEDED
                    ):

    fig, AX = pt.figure(axes=(6,2), 
                        ax_scale=(1,1), hspace=0.5,
                        wspace=0.3, right=5)

    trace_resp(d, AX[0][0], key='Pre')
    trace_resp(d, AX[1][0], key='Post')
    pt.set_plot(AX[0][0], ylabel='$\\Delta$F/F', xticks_labels=[])
    pt.set_plot(AX[1][0], 
                xlabel='time (s)', ylabel='$\\Delta$F/F')
    pt.set_common_ylims([AX[0][0], AX[1][0]])


    colors = ['tab:red', 'tab:blue', 'tab:grey']
    for l, loc in enumerate(['Pre', 'Post']):

        pt.annotate(AX[l][0], loc, (-0.2,1), ha='right', 
                    bold=True, fontsize=9)

        for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):
            im = AX[l][1+k].imshow(d['%s-%s_map' % (loc, key)],
                           cmap=pt.plt.cm.binary,
                            vmin=bounds[0], vmax=bounds[1])
            AX[l][1+k].axis('off')
            if l==0:
                AX[l][1+k].set_title(key, color=colors[k])

            AX[l][5].hist(d['%s-%s_map' % (loc,key)].flatten(),
                          color=colors[k], alpha=.5,
                           bins=np.linspace(*bounds, 50))

            pt.set_plot(AX[l][5], yticks=[], ylabel='pix. count',
                        xticks_labels=[] if l==0 else None,
                        xlabel='$\\Delta$F/F' if l==1 else '')

        pt.plt.gcf().colorbar(im, ax=AX[l][3],
                    shrink=0.9, aspect=10,
                        label='$\\Delta$F/F\n [0.5,1.5]s ')
        AX[l][4].axis('off') 

    pt.set_common_ylims([AX[0][0], AX[1][0]])
    AX[0][5].set_title(d['id'])

for d in DATA:
    for loc in ['Pre', 'Post']:
        for key in ['Ipsi', 'Contra', 'Blank']:
            d['%s-%s_map' % (loc, key)] = \
                compute_mean_map(d['t'], d['%s-%s' % (loc, key)],
                                 response_window=[0.5,1.5],)-\
                compute_mean_map(d['t'], d['%s-%s' % (loc, key)],
                                 response_window=[-1.,0.],)

    plot_mouse(d,
        bounds=[0, .5*np.max(d['Pre-Contra_map']+d['Post-Contra_map'])])

# %%

fig, AX = pt.figure(axes=(3,1), wspace=1,
                    ax_scale=(.6,1))

colors = ['tab:red', 'tab:blue', 'tab:grey']
for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):

    for d in DATA:
        AX[k].plot([0,1],
            [np.mean(d['%s-%s_map' % (loc, key)]) for loc in ['Pre', 'Post']],
            'o-', color=colors[k])
    AX[k].set_title(key, color=colors[k])
    pt.set_plot(AX[k], xlim=[-0.5,1.5], xticks=[0,1],
                xticks_labels=['Pre  ', '  Post'],
                yticks_labels=[] if k>0 else None,
                ylabel='mean $\\Delta$F/F' if k==0 else '')
pt.set_common_ylims(AX)

# %%