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
raw_data_path = \
    os.path.expanduser('/Volumes/COMMON/Group-2-ODI/')
    # os.path.expanduser('/Volumes/YANN/ODI-GluN3A/')
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
rsync -avhP --exclude "._*" --exclude "Imaging*" --exclude "NIdaq.*" --exclude "*Prelim*" /Volumes/T7\ Touch/ODI/* ~/DATA/Taddy/ODI-GluN3A/Group1/
rsync -avhP --exclude "._*" --exclude "Imaging*" --exclude "NIdaq.*" --exclude "*Prelim*" /Volumes/YANN/ODI-GluN3A/* ~/DATA/Taddy/ODI-GluN3A/Group1/
rsync -avhP --exclude "._*" --exclude "Imaging*" --exclude "NIdaq.*" --exclude "*Prelim*" /Volumes/COMMON/Group-2-ODI/Data/* ~/DATA/Taddy/ODI-GluN3A/Group2/
```
"""

# %%
import pandas as pd
raw_data_path = \
    os.path.expanduser('~/DATA/Taddy/ODI-GluN3A')
csv = pd.read_csv(os.path.join(raw_data_path, 'DataTable.csv'),
                    delimiter=';')

def load_mouse(index):

    data = {'id':csv['Subject'][index]}
    for key in ['Pre-Ipsi', 'Pre-Contra', 'Pre-Blank', 
                'Post-Ipsi', 'Post-Contra', 'Post-Blank']:
        if type(csv[key][index]) is not float:
            folder = os.path.expanduser('~/DATA/Taddy/ODI-GluN3A/'+\
                                csv['Groups'][index]+\
                                csv[key][index].replace('~',''))
            resp = np.load(os.path.join(folder, 'resp-maps.npy'),
                        allow_pickle=True).item()
            data[key] = resp['resp']

    data['t'] = resp['t']

    return data

# %%
import numpy as np
import tempfile
SCRMBL, KD = [], []
for i in np.arange(len(csv['Groups']))[\
    (csv['Groups']=='Group2') & \
    (csv['Condition']=='Scramble')]:
    SCRMBL.append(load_mouse(i))
for i in np.arange(len(csv['Groups']))[\
    (csv['Groups']=='Group2') & \
    (csv['Condition']=='KD')]:
    KD.append(load_mouse(i))

# %%

from scipy.ndimage import gaussian_filter
import plot_tools as pt
pt.set_style('dark')
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


def plot_mouse(d, label='', 
                 bounds = [0, 0.2], # ADJUST BOUNDS IF NEEDED
                    ):

    fig, AX = pt.figure(axes=(6,1), top =1.3, left=1.5, bottom=1.4,
                        ax_scale=(1,1), hspace=0.5,
                        wspace=0.3, right=5, reshape_axes=False)

    trace_resp(d, AX[0][0], key='Pre')
    pt.set_plot(AX[0][0], 
                xlabel='time (s)', ylabel='$\\Delta$F/F')

    colors = ['tab:red', 'tab:blue', 'tab:grey']
    for l, loc in enumerate(['Pre']):

        pt.annotate(AX[l][0], loc, (-0.2,1), ha='right', 
                    bold=True, fontsize=9)

        for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):
            im = AX[l][1+k].imshow(d['%s-%s_map' % (loc, key)],
                           cmap=pt.plt.cm.binary_r,
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

    AX[0][5].set_title('%s - %s' % (d['id'], label))
    return fig

n=1
for DATA, label in zip([SCRMBL, KD],
                       ['Scramble', 'Knock-Down']):
    for d in DATA:
        for loc in ['Pre']:
            for key in ['Ipsi', 'Contra', 'Blank']:
                d['%s-%s_map' % (loc, key)] = \
                    compute_mean_map(d['t'], d['%s-%s' % (loc, key)],
                                    response_window=[0.5,1.5],)-\
                    compute_mean_map(d['t'], d['%s-%s' % (loc, key)],
                                    response_window=[-1.,0.],)

        fig = plot_mouse(d, label=label,
            bounds=[0, np.max(d['Pre-Contra_map'])])
        fig.savefig(os.path.join(tempfile.gettempdir(), '%i.png' %n), 
                    transparent=False)
        n+=1

# %%
from PIL import Image

images = [Image.open(os.path.join(tempfile.gettempdir(), '%i.png' %i))\
                     for i in range(1, n)]
widths, heights = zip(*(i.size for i in images))

width = max(widths)
height = sum(heights)

new_im = Image.new('RGB', (width, height))

y_offset = 0
for im in images:
  new_im.paste(im, (0,y_offset))
  y_offset += im.size[1]

NB_path = os.path.expanduser('~/Documents/Notebook/Projects/Taddy-GluN3/figs')
new_im.save(os.path.join(NB_path, '6-jan-2026-all-OD.png'))
from IPython.display import Image 
pil_img = Image(filename=os.path.join(NB_path, '6-jan-2026-all-OD.png'))
display(pil_img)

# %%
from scipy import stats

fig, AX = pt.figure(axes=(3,1), wspace=1, top=2, left=2, 
                    ax_scale=(.9,1.3))

colors = ['tab:red', 'tab:blue', 'tab:grey']
for i, color, DATA, label in zip(range(2), 
                                 ['tab:green', 'tab:orange'],
                                 [SCRMBL, KD],
                       ['Scramble', 'Knock-Down']):
    pt.annotate(AX[0], label+'  '+i*'\n', (0, 1), 
                color=color, ha='right')
    for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):

        for d in DATA:
            AX[k].plot([2*i+.2],
                [np.mean(d['%s-%s_map' % (loc, key)]) for loc in ['Pre']],
                'o', color=color, lw=0.5,ms=1)
        final = {}
        for l,  loc in enumerate(['Pre']):
            final[loc] =[np.mean(d['%s-%s_map' % (loc, key)]) for d in DATA]
            pt.scatter([2*i+l], [np.mean(final[loc])], ax=AX[k],
                       sy=stats.sem(final[loc]), color=color)
        # pt.annotate(AX[k], 
        #             pt.from_pval_to_star(stats.wilcoxon(final['Pre'], final['Post']).pvalue),
        #             (0.1+i*0.5, 1), color=color)

        AX[k].set_title(key+'\n', color=colors[k])

        pt.set_plot(AX[k], xlim=[-0.5,3.5], xticks=[0,1,2,3],
                    xticks_labels=['pre', 'post', 'pre', 'post'],
                    xticks_rotation=90,
                    # xticks_labels=[],
                    yticks_labels=[] if k>0 else None,
                    ylabel='mean $\delta$ $\\Delta$F/F' if k==0 else '')
        
pt.set_common_ylims(AX)

fig.savefig(os.path.join(NB_path, '6-jan-2026-summary-OD.png'),
            transparent=False)


# %%

















# %%
import numpy as np
import tempfile
SCRMBL, KD = [], []
for i in np.arange(len(csv['Groups']))[\
    (csv['Groups']=='Group1') & \
    (csv['Condition']=='Scramble') & \
    (csv['Full 3 days MD']=='Yes')]:
    SCRMBL.append(load_mouse(i))
for i in np.arange(len(csv['Groups']))[\
    (csv['Groups']=='Group1') & \
    (csv['Condition']=='KD') & \
    (csv['Full 3 days MD']=='Yes')]:
    KD.append(load_mouse(i))

# %%
from scipy.ndimage import gaussian_filter
import plot_tools as pt
pt.set_style('dark')
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


def plot_mouse(d, label='', 
                 bounds = [0, 0.2], # ADJUST BOUNDS IF NEEDED
                    ):

    fig, AX = pt.figure(axes=(6,2), top =1.3, left=1.5, bottom=1.4,
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
                           cmap=pt.plt.cm.binary_r,
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
    AX[0][5].set_title('%s - %s' % (d['id'], label))
    return fig

n=1
for DATA, label in zip([SCRMBL, KD],
                       ['Scramble', 'Knock-Down']):
    for d in DATA:
        for loc in ['Pre', 'Post']:
            for key in ['Ipsi', 'Contra', 'Blank']:
                d['%s-%s_map' % (loc, key)] = \
                    compute_mean_map(d['t'], d['%s-%s' % (loc, key)],
                                    response_window=[0.5,1.5],)-\
                    compute_mean_map(d['t'], d['%s-%s' % (loc, key)],
                                    response_window=[-1.,0.],)

        fig = plot_mouse(d, label=label,
            bounds=[0, .5*np.max(d['Pre-Contra_map']+d['Post-Contra_map'])])
        fig.savefig(os.path.join(tempfile.gettempdir(), '%i.png' %n), 
                    transparent=False)
        n+=1

# %%
from PIL import Image

images = [Image.open(os.path.join(tempfile.gettempdir(), '%i.png' %i))\
                     for i in range(1, n)]
widths, heights = zip(*(i.size for i in images))

width = max(widths)
height = sum(heights)

new_im = Image.new('RGB', (width, height))

y_offset = 0
for im in images:
  new_im.paste(im, (0,y_offset))
  y_offset += im.size[1]

NB_path = os.path.expanduser('~/Documents/Notebook/Projects/Taddy-GluN3/figs')
new_im.save(os.path.join(NB_path, '30-dec-2025-all-OD.png'))
from IPython.display import Image 
pil_img = Image(filename=os.path.join(NB_path, '30-dec-2025-all-OD.png'))
display(pil_img)

# %%
from scipy import stats

fig, AX = pt.figure(axes=(3,1), wspace=1, top=2, left=2, 
                    ax_scale=(.9,1.3))

colors = ['tab:red', 'tab:blue', 'tab:grey']
for i, color, DATA, label in zip(range(2), 
                                 ['tab:green', 'tab:orange'],
                                 [SCRMBL, KD],
                       ['Scramble', 'Knock-Down']):
    pt.annotate(AX[0], label+'  '+i*'\n', (0, 1), 
                color=color, ha='right')
    for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):

        for d in DATA:
            AX[k].plot([2*i,2*i+1],
                [np.mean(d['%s-%s_map' % (loc, key)]) for loc in ['Pre', 'Post']],
                '-', color=color, lw=0.5)
        final = {}
        for l,  loc in enumerate(['Pre', 'Post']):
            final[loc] =[np.mean(d['%s-%s_map' % (loc, key)]) for d in DATA]
            pt.scatter([2*i+l], [np.mean(final[loc])], ax=AX[k],
                       sy=stats.sem(final[loc]), color=color)
        pt.annotate(AX[k], 
                    pt.from_pval_to_star(stats.wilcoxon(final['Pre'], final['Post']).pvalue),
                    (0.1+i*0.5, 1), color=color)


        AX[k].set_title(key+'\n', color=colors[k])

        pt.set_plot(AX[k], xlim=[-0.5,3.5], xticks=[0,1,2,3],
                    xticks_labels=['pre', 'post', 'pre', 'post'],
                    xticks_rotation=90,
                    # xticks_labels=[],
                    yticks_labels=[] if k>0 else None,
                    ylabel='mean $\delta$ $\\Delta$F/F' if k==0 else '')
        
pt.set_common_ylims(AX)

fig.savefig(os.path.join(NB_path, '30-dec-2025-summary-OD.png'),
            transparent=False)

# %%
import tempfile
fig.savefig(os.path.join(tempfile.gettempdir(), '1.png'), transparent=False)
# %%

# %% [markdown]

Now just the Pre maps



# %%
import numpy as np

raw_data_path = \
    os.path.expanduser('~/DATA/Taddy/ODI-GluN3A')
csv = pd.read_csv(os.path.join(raw_data_path, 'DataTable.csv'),
                    delimiter=';')

def load_mouse(index):

    data = {'id':csv['Subject'][index]}
    for key in ['Pre-Ipsi', 'Pre-Contra', 'Pre-Blank']:
        folder = os.path.expanduser('~/DATA/Taddy/ODI-GluN3A'+\
                              csv[key][index].replace('~',''))
        resp = np.load(os.path.join(folder, 'resp-maps.npy'),
                    allow_pickle=True).item()
        data[key] = resp['resp']

    data['t'] = resp['t']

    return data

SCRMBL, KD = [], []
for i in np.arange(len(csv['Groups']))[\
    (csv['Condition']=='Scramble')]:
    SCRMBL.append(load_mouse(i))
for i in np.arange(len(csv['Groups']))[\
    (csv['Condition']=='KD')]:
    KD.append(load_mouse(i))


# %%

def plot_mouse(d, label='', 
                 bounds = [0, 0.2], # ADJUST BOUNDS IF NEEDED
                    ):

    fig, AX = pt.figure(axes=(6,1), top =1.3, left=1.5, bottom=1.4,
                        ax_scale=(1,1), hspace=0.5,
                        wspace=0.3, right=5, 
                        reshape_axes=False)

    trace_resp(d, AX[0][0], key='Pre')
    pt.set_plot(AX[0][0], 
                xlabel='time (s)', ylabel='$\\Delta$F/F')


    colors = ['tab:red', 'tab:blue', 'tab:grey']

    l, loc = 0, 'Pre'

    pt.annotate(AX[l][0], loc, (-0.2,1), ha='right', 
                bold=True, fontsize=9)

    for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):
        im = AX[l][1+k].imshow(d['%s-%s_map' % (loc, key)],
                        cmap=pt.plt.cm.binary_r,
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

    AX[0][5].set_title('%s - %s' % (d['id'], label))

    return fig

pt.set_style('dark')
n=1
for DATA, label in zip([SCRMBL, KD],
                       ['Scramble', 'Knock-Down']):
    for d in DATA:
        for loc in ['Pre']:
            for key in ['Ipsi', 'Contra', 'Blank']:
                d['%s-%s_map' % (loc, key)] = \
                    compute_mean_map(d['t'], d['%s-%s' % (loc, key)],
                                    response_window=[0.5,1.5],)-\
                    compute_mean_map(d['t'], d['%s-%s' % (loc, key)],
                                    response_window=[-1.,0.],)

        fig = plot_mouse(d, label=label,
            bounds=[0, np.max(d['Pre-Contra_map'])])
        fig.savefig(os.path.join(tempfile.gettempdir(), '%i.png' %n), 
                    transparent=False)
        n+=1

# %%
from PIL import Image

images = [Image.open(os.path.join(tempfile.gettempdir(), '%i.png' %i))\
                     for i in range(1, n)]
widths, heights = zip(*(i.size for i in images))

width = max(widths)
height = sum(heights)

new_im = Image.new('RGB', (width, height))

y_offset = 0
for im in images:
  new_im.paste(im, (0,y_offset))
  y_offset += im.size[1]

new_im.save(os.path.expanduser(\
    '~/Documents/Notebook/Projects/Taddy-GluN3/figs/30-dec-2025-all-Pre-OD.png'))
from IPython.display import Image 
pil_img = Image(filename=os.path.expanduser(\
    '~/Documents/Notebook/Projects/Taddy-GluN3/figs/30-dec-2025-all-Pre-OD.png'))
display(pil_img)

# %%
from scipy import stats

fig, AX = pt.figure(axes=(3,1), wspace=1, top=2, left=2, 
                    ax_scale=(.9,1.3))

final = {}
colors = ['tab:red', 'tab:blue', 'tab:grey']
for i, color, DATA, label in zip(range(2), 
                                 ['tab:green', 'tab:orange'],
                                 [SCRMBL, KD],
                       ['Scramble', 'Knock-Down']):
    pt.annotate(AX[0], label+'  '+i*'\n', (0, 1), 
                color=color, ha='right')
    for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):

        for d in DATA:
            AX[k].plot([2*i+np.random.uniform(-0.2,0.2)],
                [np.mean(d['%s-%s_map' % ('Pre', key)])],
                'o', color=color, ms=1)

        for l,  loc in enumerate(['Pre']):
            final['%s-%s-%s' % (label,loc,key)] =\
                    [np.mean(d['%s-%s_map' % (loc, key)]) for d in DATA]
            pt.scatter([2*i+l], 
                       [np.mean(final['%s-%s-%s' % (label,loc,key)])], 
                       sy=[stats.sem(final['%s-%s-%s' % (label,loc,key)])], 
                        ax=AX[k], color=color)

        AX[k].set_title(key+'\n', color=colors[k])

        pt.set_plot(AX[k], xlim=[-0.5,3.5], xticks=[0,1,2,3],
                    xticks_labels=['pre', 'post', 'pre', 'post'],
                    xticks_rotation=90,
                    # xticks_labels=[],
                    yticks_labels=[] if k>0 else None,
                    ylabel='mean $\delta$ $\\Delta$F/F' if k==0 else '')

for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):
    pt.annotate(AX[k], 
                pt.from_pval_to_star(stats.ttest_ind(\
                                    final['%s-Pre-%s' % ('Scramble',key)], 
                                    final['%s-Pre-%s' % ('Knock-Down',key)]).pvalue),
                (.2, 1))

        
pt.set_common_ylims(AX)
fig.savefig(os.path.join(NB_path, '30-dec-2025-summary-Pre-OD.png'),
            transparent=True)
# %%
