# %%
import pandas as pd
import os, sys
sys.path += ['physion/src']
import numpy as np
import physion.utils.plot_tools as pt
from scipy.ndimage import gaussian_filter, gaussian_filter1d

raw_data_path = \
    os.path.expanduser('~/DATA/Taddy/ODI-GluN3A/')
    # os.path.expanduser('/Volumes/COMMON/Group-2-ODI/')
    # os.path.expanduser('/Volumes/YANN/ODI-GluN3A/')
    # os.path.expanduser('/Volumes/T7 Touch/ODI')

csv = pd.read_csv(\
    os.path.expanduser('~/DATA/Taddy/ODI-GluN3A/DataTable.csv'),
                    delimiter=';')
NB_path = os.path.expanduser('~/Documents/Notebook/Projects/Taddy-GluN3/figs')

summary_folder = os.path.expanduser(\
    '~/Library/CloudStorage/OneDrive-ICM/DATA/Taddy/Ocular-Dominance-WT-GluN3KO')

pt.set_style('dark')
WINDOW, SUFFIX = [0.1, 0.6], ''
WINDOW, SUFFIX = [0.1, 2.0], '-2s'

# %%

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

# %%

if False:

    raw_data_path = \
        os.path.join('/Volumes', 'T7 Touch', 'ODI-GluN3A', 'raw')
        # os.path.expanduser('~/DATA/Taddy/ODI-GluN3A/raw')

    smoothing = (0,4,4)
    for k, v, _ in os.walk(raw_data_path):
        if 'ImagingCamera-imgs' in v:
            folder = k
            # if ('2025_12_27' in k): # or ('2025_12_20' in k):
            if '2025_12_26' in k:
                print(k)
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
current:
```
rsync -avhP --exclude "._*" --exclude "Imaging*" --exclude "NIdaq.*" --exclude "*Prelim*" /Volumes/T7\ Touch/ODI-GluN3A/raw/* ~/DATA/Taddy/ODI-GluN3A/raw
```
"""

"""
old:
```
rsync -avhP --exclude "._*" --exclude "Imaging*" --exclude "NIdaq.*" --exclude "*Prelim*" /Volumes/T7\ Touch/ODI-GluN3A/* ~/DATA/Taddy/ODI-GluN3A/Group1/
rsync -avhP --exclude "._*" --exclude "Imaging*" --exclude "NIdaq.*" --exclude "*Prelim*" /Volumes/YANN/ODI-GluN3A/* ~/DATA/Taddy/ODI-GluN3A/Group1/
rsync -avhP --exclude "._*" --exclude "Imaging*" --exclude "NIdaq.*" --exclude "*Prelim*" /Volumes/COMMON/Group-2-ODI/Data/* ~/DATA/Taddy/ODI-GluN3A/Group2/
```
"""

# %%
raw_data_path = \
    os.path.expanduser('~/DATA/Taddy/ODI-GluN3A')
csv = pd.read_csv(os.path.join(raw_data_path, 'DataTable.csv'),
                    delimiter=';')

def load_mouse(index):

    data = {'id':csv['Subject'][index], 'index':index}
    for key in ['Pre-Ipsi', 'Pre-Contra', 'Pre-Blank', 
                'Post-Ipsi', 'Post-Contra', 'Post-Blank']:
        if type(csv[key][index]) is not float:
            folder = os.path.expanduser('~/DATA/Taddy/ODI-GluN3A/raw'+\
                                # csv['Groups'][index]+\
                                csv[key][index].replace('~',''))
            resp = np.load(os.path.join(folder, 'resp-maps.npy'),
                        allow_pickle=True).item()
            data[key] = resp['resp']

    data['t'] = resp['t']

    return data

# %%
import tempfile
SCRMBL_IDS = np.arange(len(csv['Subject']))[(csv['Condition']=='Scramble')]
KD_IDS = np.arange(len(csv['Subject']))[(csv['Condition']=='KD')]

# SCRMBL, KD = [], []
# for i in np.arange(len(csv['Subject']))[\
#     (csv['Condition']=='Scramble')]:
#     SCRMBL.append(load_mouse(i))
# for i in np.arange(len(csv['Subject']))[\
#     (csv['Condition']=='KD')]:
#     KD.append(load_mouse(i))

# %%


def preprocess_maps(d, 
                    baseline_window=[-1,0.1],
                    response_window=WINDOW,
                    smoothing=4):
    
    for loc in ['Pre', 'Post']:
        for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):

            # response window
            cond = (d['t']>response_window[0]) & (d['t']<response_window[1])
            d['%s-%s_map' % (loc, key)] = \
                gaussian_filter(\
                    d['%s-%s' % (loc, key)][cond, :,:].mean(axis=0),
                    smoothing)

            # baseline window
            cond = (d['t']>baseline_window[0]) & (d['t']<baseline_window[1])
            d['%s-%s_baseline' % (loc, key)] = \
                gaussian_filter(\
                    d['%s-%s' % (loc, key)][cond, :,:].mean(axis=0),
                    smoothing)

            # F0
            d['%s-%s_dResp' % (loc, key)] = d['%s-%s_map' % (loc, key)]-\
                                    d['%s-%s_baseline' % (loc, key)]
            
            # dFoF
            d['%s-%s_dFoF' % (loc, key)] = 100. * d['%s-%s_dResp' % (loc, key)]/\
                                    d['%s-%s_baseline' % (loc, key)]

    
def trace_resp(d, ax, 
               key='Pre-',
               data='raw',
               loc='mean', W=100,
               F0_percentile=30.,
               Tsmoothing=1):

    for key, color in zip(\
        ['%s-Ipsi' % key, '%s-Contra' % key, '%s-Blank' % key],
        ['tab:red', 'tab:blue', 'tab:grey']):

        map = d[key+'_map']
        Resp = d[key]
        t = d['t']

        if loc=='max':
            # mean at local maximum, 
            i0, i1 = np.unravel_index(np.argmax(map), np.array(map).shape)
            resp = Resp[:,i0-W:i0+W,i1-W:i1+W].mean(axis=(1,2))
        elif loc=='mean':
            # temporal mean over the whole image
            resp = Resp.mean(axis=(1,2))

        if data=='dFoF':
            F0 = np.mean(d[key+'_baseline']) # using the baseline as F0
            resp = (resp-F0)/F0

        resp[0] = resp[1]

        resp = gaussian_filter1d(resp, Tsmoothing)

        ax.plot(t[1:-1], resp[1:-1], color=color)


def plot_mouse(d, window, label='', 
               data = 'raw',
                 bounds = None, #[0, 0.2], # ADJUST BOUNDS IF NEEDED
                    ):

    fig, AX = pt.figure(axes=(6,2), top =1.3, left=1.5, bottom=1.4,
                        ax_scale=(1.4,1), hspace=0.5,
                        wspace=0.1, right=5, reshape_axes=False)

    if data=='dFoF':
        Label = '$\\Delta$F/F (%)'
        Map='dFoF'
    else:
        Label = data
        Map='map'

    colors = ['tab:red', 'tab:blue', 'tab:grey']
    for l, loc in enumerate(['Pre', 'Post']):

        pt.annotate(AX[l][0], loc, (-0.2,1), ha='right', 
                    bold=True, fontsize=9)
        
        trace_resp(d, AX[l][0], data=data, key=loc)
        pt.set_plot(AX[l][0], 
                    xlabel='time (s)' if l==1 else None, ylabel=Label)

        bounds = [\
            1.1*np.min([d['%s-%s_%s' % (loc, key, Map)]\
                    for key in ['Ipsi', 'Contra', 'Blank']]),
            1.0*np.max([d['%s-%s_%s' % (loc, key, Map)]\
                    for key in ['Ipsi', 'Contra', 'Blank']])
        ]

        for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):
            im = AX[l][1+k].imshow(d['%s-%s_%s' % (loc, key, Map)],
                           cmap=pt.plt.cm.binary_r,
                            vmin=bounds[0], vmax=bounds[1])
            AX[l][1+k].axis('off')
            if l==0:
                AX[l][1+k].set_title(key, color=colors[k])

            AX[l][5].hist(d['%s-%s_%s' % (loc,key,Map)].flatten(),
                          color=colors[k], alpha=.5,
                           bins=np.linspace(*bounds, 50))

            pt.set_plot(AX[l][5], yticks=[], ylabel='pix. count',
                        xticks_labels=[] if l==0 else None,
                        xlabel=Label if l==1 else '')

        pt.plt.gcf().colorbar(im, ax=AX[l][3],
                    shrink=0.9, aspect=10,
                        label='%s\n[%.1f,%.1f]' % (Label,
                                                  window[0], window[1]))
        AX[l][4].axis('off') 
    pt.set_common_xlims([AX[0][5], AX[1][5]])

    AX[0][5].set_title('%i) %s - %s' % (d['index'], d['id'], label))
    return fig

nData_max = 100 # put to 100 to have all data

from PIL import Image

def plot_all(
        data = 'raw',
        window = WINDOW,
        figname=None,
        ):

    n=1
    for IDS, label in zip([SCRMBL_IDS, KD_IDS],
                        ['Scramble', 'Knock-Down']):
        for id in IDS[:nData_max]:
            d = load_mouse(id)
            for loc in ['Pre', 'Post']:
                for key in ['Ipsi', 'Contra', 'Blank']:
                    # load resp:
                    resp = d['%s-%s' % (loc, key)]
                    # window cond
                    preprocess_maps(d)

            fig = plot_mouse(d, 
                            data=data,
                            window=window,
                            #  bounds=[0, 0.4],
                            label=label)
            fig.savefig(os.path.join(tempfile.gettempdir(), '%i.png' %n), 
                        transparent=False)
            pt.plt.close(fig)
            n+=1

    if figname is not None:
        # build a merged-figure
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
        new_im.save(os.path.join(NB_path, figname))

plot_all(data='raw', 
         figname='OD-exp-raw-data-all%s.png' % SUFFIX)

# %%
plot_all(data='dFoF', 
         figname='OD-exp-dFoF-all%s.png' % SUFFIX)

# %%

if False:
    from IPython.display import Image as ImageD
    pil_img = ImageD(filename=\
                    os.path.join(NB_path, 'OD-exp-raw-data-all%s.png' % SUFFIX))
    display(pil_img)

# %% [markdown]
## Illustrate the preprocessing steps

# %%

fig, AX = pt.figure(axes=(3,4), top =2.3, left=2.5, bottom=1.4,
                    ax_scale=(1.1,1), hspace=0.5,
                    wspace=0.3, right=5, reshape_axes=False)
data = load_mouse(4) # change below:
fig.suptitle('"Pre" recording, 4) Mouse 1, Knock-Down')

colors = ['tab:red', 'tab:blue', 'tab:grey']


preprocess_maps(data,
                baseline_window=[-1,0],
                response_window=WINDOW)

## Baseline
pt.annotate(AX[0][0], 'Baseline Map (F0)\n [-1,0.1]s interval', 
            (-0.2,0.1), ha='right', fontsize=8)
pt.annotate(AX[1][0], 'Response Map\n [0.1,0.6]s interval', 
            (-0.2,0.1), ha='right', fontsize=8)
pt.annotate(AX[2][0], 'Response-Baseline Map\n [0.1,0.6]s interval', 
            (-0.2,0.1), ha='right', fontsize=8)
pt.annotate(AX[3][0], '$\Delta F /F (%) $ \n (Resp.-Bas.)/Bas.', 
            (-0.2,0.1), ha='right', fontsize=8)

loc='Pre'
for t, typ in enumerate(['map', 'baseline', 'dResp', 'dFoF']):
    bounds = [\
        1.1*np.min([data['%s-%s_%s' % (loc, key, typ)]\
                for key in ['Ipsi', 'Contra', 'Blank']]),
        1.0*np.max([data['%s-%s_%s' % (loc, key, typ)]\
                for key in ['Ipsi', 'Contra', 'Blank']])
    ]
    for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):
        im = AX[t][k].imshow(data['%s-%s_%s' % (loc, key, typ)],
                        cmap=pt.plt.cm.binary_r,
                        vmin=bounds[0], vmax=bounds[1])
        AX[t][k].axis('off')
        AX[t][k].set_title(key, color=colors[k])
    fig.colorbar(im, ax=AX[t][2], shrink=0.9, aspect=10,
                    label='raw Fluo.' if t<3 else '$\Delta F /F $ (%) ')

fig.savefig(os.path.join(NB_path, 'OD-exp-Preprocessing%s.png' % SUFFIX),
            transparent=True)


# %%
from scipy import stats

fig, AX = pt.figure(axes=(3,1), wspace=1, top=2, left=2, 
                    ax_scale=(.9,1.3))

colors = ['tab:red', 'tab:blue', 'tab:grey']
final = {}
for i, color, IDS, label in zip(range(2), 
                                 ['tab:green', 'tab:orange'],
                                 [SCRMBL_IDS, KD_IDS],
                                 ['Scramble', 'Knock-Down']):
    pt.annotate(AX[0], label+'  '+i*'\n', (0, 1), 
                color=color, ha='right')

    final[label] = {}
    for loc in ['Pre', 'Post']:
        final[label][loc] = {}
        for key in ['Ipsi', 'Contra', 'Blank']:
            final[label][loc][key] = []


    for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):

        for id in IDS:

            d = load_mouse(id)
            preprocess_maps(d)

            AX[k].plot([2*i-.1, 2*i+1+.2],
                [np.mean(d['%s-%s_dFoF' % (loc, key)]) for loc in ['Pre', 'Post']],
                '-', color=color, lw=0.5)

            for l,  loc in enumerate(['Pre', 'Post']):
                final[label][loc][key].append(\
                            np.mean(d['%s-%s_dFoF' % (loc, key)]))

        for l,  loc in enumerate(['Pre', 'Post']):
            pt.scatter([2*i+l], [np.mean(final[label][loc][key])], ax=AX[k],
                       sy=stats.sem(final[label][loc][key]), color=color)
        pt.annotate(AX[k], 
                    pt.from_pval_to_star(stats.wilcoxon(final[label]['Pre'][key], final[label]['Post'][key]).pvalue),
                    (0.1+i*0.5, 1), color=color)

        AX[k].set_title(key+'\n', color=colors[k])

        pt.set_plot(AX[k], xlim=[-0.5,3.5], xticks=[0,1,2,3],
                    xticks_labels=['pre', 'post', 'pre', 'post'],
                    xticks_rotation=90,
                    yticks_labels=[] if k>0 else None,
                    ylabel='mean $\\Delta$F/F (%)' if k==0 else '')
        
pt.set_common_ylims(AX)

fig.savefig(os.path.join(NB_path, 'OD-exp-summary-1%s.png' % SUFFIX),
            transparent=False)


# %%
from scipy import stats

fig, AX = pt.figure(axes=(2,1), wspace=1, top=2, left=2, 
                    ax_scale=(1.1,1.3))

for i, color, IDS, label in zip(range(2), 
                                 ['tab:green', 'tab:orange'],
                                 [SCRMBL_IDS, KD_IDS],
                                 ['Scramble', 'Knock-Down']):

    pt.annotate(AX[0], label+'  '+i*'\n', (0, 1), 
                color=color, ha='right')

    for l,  loc in enumerate(['Pre', 'Post']):

        for f1, f2, f3 in zip(
            final[label][loc]['Ipsi'],
            final[label][loc]['Contra'],
            final[label][loc]['Blank']):
            AX[l].plot([3*i-.2, 3*i+1-0.1, 3*i+2+.2],
                    [f1, f2, f3], '-', color=color, lw=0.5)

        for k, key in enumerate(['Ipsi', 'Contra', 'Blank']):
            pt.scatter([3*i+k], [np.mean(final[label][loc][key])], ax=AX[l],
                        sy=stats.sem(final[label][loc][key]), color=color)

        # for l,  loc in enumerate(['Pre', 'Post']):
        pt.annotate(AX[l], 
                    pt.from_pval_to_star(stats.wilcoxon(final[label][loc]['Ipsi'], final[label][loc]['Contra']).pvalue),
                    (3*i, 6), color=color, xycoords='data')
        pt.annotate(AX[l], 
                    pt.from_pval_to_star(stats.wilcoxon(final[label][loc]['Blank'], final[label][loc]['Contra']).pvalue),
                    (3*i+1.5, 6), color=color, xycoords='data')

        AX[l].set_title(loc+'\n')

        pt.set_plot(AX[l], xlim=[-0.5,6.5], xticks=range(6),
                    xticks_labels=['ipsi', 'contra', 'blank','ipsi', 'contra', 'blank'],
                    xticks_rotation=90,
                    yticks_labels=[] if l>0 else None,
                    ylabel='mean $\\Delta$F/F (%)' if l==0 else '')
        
pt.set_common_ylims(AX)

fig.savefig(os.path.join(NB_path, 'OD-exp-summary-2%s.png' % SUFFIX),
            transparent=False)


# %%
from scipy import stats

fig, ax = pt.figure(ax_scale=(1.1,1.3), top=2, left=5)

fig.suptitle('Ocular-Dominance index\n(C-I)/(C+I), $\Delta$F/F clipped to >0')

for i, color, label in zip(range(2), 
                            ['tab:green', 'tab:orange'],
                            ['Scramble', 'Knock-Down']):
    
    for l,  loc in enumerate(['Pre', 'Post']):

        final['OD-%s-%s' % (label, loc)] = \
            (\
                np.clip(final[label][loc]['Contra'], 1e-3, np.inf)-
                np.clip(final[label][loc]['Ipsi'], 1e-3, np.inf)
            )/\
            (\
                np.clip(final[label][loc]['Contra'], 1e-3, np.inf)+
                np.clip(final[label][loc]['Ipsi'], 1e-3, np.inf)
            )

    for o1, o2 in zip(final['OD-%s-%s' % (label, 'Pre')],
                        final['OD-%s-%s' % (label, 'Post')]):
        ax.plot([2*i-.1, 2*i+1+.2],
                [o1, o2], '-', color=color, lw=0.5)

    for l,  loc in enumerate(['Pre', 'Post']):
        pt.scatter([2*i+l], [np.mean(final['OD-%s-%s' % (label, loc)])], 
                   ax=ax,
                    sy=stats.sem(final['OD-%s-%s' % (label, loc)]),
                      color=color)

    pt.annotate(ax, pt.from_pval_to_star(\
                    stats.wilcoxon(
                            final['OD-%s-%s' % (label, 'Pre')],
                            final['OD-%s-%s' % (label, 'Post')]).pvalue),
                (0.1+i*0.5, 1), color=color)

    pt.annotate(ax, label+' (N=%i)'%len(final['OD-%s-%s' % (label, 'Pre')])+\
                '  '+i*'\n', (0, 1), 
                color=color, ha='right')


pt.set_plot(ax, xlim=[-0.5,3.5], xticks=[0,1,2,3],
            xticks_labels=['pre', 'post', 'pre', 'post'],
            xticks_rotation=90,
            ylabel='OD index')

fig.savefig(os.path.join(NB_path, 'OD-exp-summary%s.png' % SUFFIX),
            transparent=False)

# %%
import itertools
for label in ['Scramble', 'Knock-Down']:
    DF = pd.DataFrame()
    for when, where in itertools.product(['Pre', 'Post'], ['Ipsi', 'Contra', 'Blank']):
        DF['%s-%s' % (when, where)] = final[label][when][where]
    DF.to_excel(os.path.join(summary_folder, '%s_resp%s.xlsx' % (label, SUFFIX)))
# %%
