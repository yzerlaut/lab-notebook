# %%
import pandas as pd

xlsx = pd.ExcelFile(\
    os.path.expanduser('~/DATA/Taddy/ODI-GluN3A/DataTable.xlsx'))
sheet = xlsx.parse(0)


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

def load_mouse(index, sheet):

    title = '%s - %s ' % (sheet['Subject'][i], sheet['Condition'][i])

    ipsiFolder = '~/DATA/Taddy/ODI-GluN3A/%s/%s' % (sheet['Subject'][i], sheet['Ipsi'][i].split('/')[-1])
    contraFolder = '~/DATA/Taddy/ODI-GluN3A/%s/%s' % (sheet['Subject'][i], sheet['Contra'][i].split('/')[-1])
    blankFolder = '~/DATA/Taddy/ODI-GluN3A/%s/%s' % (sheet['Subject'][i], sheet['Blank'][i].split('/')[-1])
    t, Ipsi = compute_resp(os.path.expanduser(ipsiFolder))
    t, Contra= compute_resp(os.path.expanduser(contraFolder))
    t, Blank= compute_resp(os.path.expanduser(blankFolder))

    return {'t':t,
            'contra':Contra,
            'ipsi':Ipsi,
            'blank':Blank}

data = []
for i in range(len(sheet['Subject'])):
    data.append(load_mouse(i, sheet))


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
               W=6):

    for key, color in zip(\
        ['ipsi', 'contra', 'blank'],
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

    pt.set_plot(ax, xlabel='time (s)',
                ylabel='$\\Delta$F/F')

def plot_mouse(d, AX,
                bounds = [0, 0.2], # ADJUST BOUNDS IF NEEDED
                    ):

    trace_resp(d, AX[0])

    for ax, Map, title, color in zip(AX[1:], 
                            ['ipsi_map', 'contra_map', 'blank_map'],
                            ['ipsi', 'contra', 'blank'],
                            ['tab:red', 'tab:blue', 'tab:grey']):
        im = ax.imshow(d[Map], cmap=pt.plt.cm.binary,
                        vmin=bounds[0], vmax=bounds[1])
        ax.axis('off')
        ax.set_title(title, color=color)

    pt.plt.gcf().colorbar(im, ax=AX[3],
                shrink=0.9, aspect=10,
                    label='$\\Delta$F/F\n mean [0.5,1]s ')

    AX[4].axis('off') 

    AX[5].hist(d['ocular-dominance'].flatten(),
                bins=np.linspace(-1, 1, 150))
    # AX[5].set_xlabel('OD index')
    AX[5].set_ylabel('pix. count')
    AX[5].set_yticks([])
    AX[5].set_title('mean OD index: %.2f' % \
            np.nanmean(d['ocular-dominance']))

    im = AX[6].imshow(d['ocular-dominance'],
                        cmap=pt.plt.cm.twilight, vmin=-0.5, vmax=0.5)
    cbar = pt.plt.gcf().colorbar(im, ax=AX[6],
                        ticks=[-0.5, 0, 0.5], 
                        shrink=0.9, aspect=10, label='OD index')
    for ax in AX[1:5]+[AX[6]]:
        ax.axis('off') 

for d in data:
    d['ipsi_map'] = compute_mean_map(d['t'], d['ipsi'],
                                     response_window=[0.5,1.5],)-\
                    compute_mean_map(d['t'], d['ipsi'],
                                     response_window=[-1.,0.],)

    d['contra_map'] = compute_mean_map(d['t'], d['contra'],
                                     response_window=[0.5,1.5],)-\
                    compute_mean_map(d['t'], d['contra'],
                                     response_window=[-1.,0.],)
    d['blank_map'] = compute_mean_map(d['t'], d['blank'],
                                     response_window=[0.5,1.5],)-\
                    compute_mean_map(d['t'], d['contra'],
                                     response_window=[-1.,0.],)
    build_OD_maps(d, threshOD=0.85)
    fig, AX = pt.figure(axes=(7,1), ax_scale=(1,1), wspace=0.3, right=5)
    plot_mouse(d, AX, bounds=[0, np.max(d['contra_map'])])



# %%

fig, AX = pt.figure(axes=(7,len(data)), ax_scale=(1,1), 
                    hspace=1.5, wspace=0.3, right=5)
for i, d in enumerate(data):
    build_OD_maps(d, threshOD=0.9)
    pt.annotate(AX[i][0], sheet['Subject'][i], (0,1.2), ha='right')
    plot_mouse(d, AX[i], bounds=[0, np.max(d['contra_map'])])

# %%
ODs = np.array([np.nanmean(d['ocular-dominance'])\
                    for d in data])
KD = np.array([sheet['Condition'][i]=='KD'\
               for i in range(len(data))])

fig, ax = pt.figure()

pt.violin(ODs, x=[0], color='k', ax=ax)
pt.scatter(np.random.uniform(-.1,.1,len(ODs)), ODs, color='k', ax=ax, ms=2)
pt.violin(ODs[KD], x=[1], color='k', ax=ax)
pt.scatter(1+np.random.uniform(-.1,.1,len(ODs[KD])), ODs[KD], color='k', ax=ax, ms=2)
pt.violin(ODs[~KD], x=[2], color='k', ax=ax)
pt.scatter(2+np.random.uniform(-.1,.1,len(ODs[~KD])), ODs[~KD], color='k', ax=ax, ms=2)
ylim=ax.get_ylim()

ax.plot([1,2], ylim[1]*np.ones(2), 'k-')
pt.annotate(ax, \
    pt.from_pval_to_star(stats.mannwhitneyu(ODs[KD], ODs[~KD]).pvalue),
    (1.5, ylim[1]), ha='center',
    xycoords='data')

stats.mannwhitneyu
pt.set_plot(ax, ylabel='OD index', 
            title='All: %.2f $\pm$ %.2f ' % (np.mean(ODs), stats.sem(ODs)),
            xticks=[0,1,2], 
            xticks_labels=['All', 'KD', 'Ctrl'],
            xticks_rotation=60)

# %%
