# %%
import os, sys, json
import numpy as np
sys.path += ['physion/src']
from physion.assembling.dataset import read_spreadsheet
from physion.utils import plot_tools as pt 
pt.set_style('dark')
from spikeinterface import full as si

# %%
datafolder = os.path.expanduser('~/DATA/Sally/2026_06_09').replace('/', os.path.sep)

# load datatable
datatable, _, _ = read_spreadsheet(\
                    os.path.join(datafolder, 'DataTable.xlsx'),
                            get_metadata_from='files')

# %%
# load open ephys
recFull = si.read_openephys(os.path.join(datafolder, '2026-04-24_12-23-16'),
                        stream_name='Record Node 101#OneBox-100.ProbeA')

# %%
# choose recording (from the datatable)

iRec = 1 

# loading the nidaq data for that protocol
nidaq = np.load(os.path.join(datafolder, datatable['time'][iRec], 'NIdaq.npy'), 
                allow_pickle=True).item()
t_nidaq = np.arange(len(nidaq['digital'][0]))*nidaq['dt']

LED = nidaq['digital'][4] # channel 4 is LED

# the alignement points:
nStart, nStop = datatable['nStart'][iRec], datatable['nStop'][iRec]

# we keep only the sub-part of the ephys corresponding to that protocol
rec = recFull.frame_slice(nStart, nStop)

t_ephys = np.linspace(0, t_nidaq[-1], nStop-nStart)

with open(os.path.join(datafolder, datatable['time'][iRec], 'metadata.json'), 'r') as f:
    metadata = json.load(f)

# loading the visual-stim data for that protocol
visStim = np.load(os.path.join(datafolder, datatable['time'][iRec], 'visual-stim.npy'), 
                allow_pickle=True).item()
visual_stim = np.zeros(len(t_nidaq), dtype=bool)
for start, stop in zip(visStim['time_start'], visStim['time_stop']):
    cond = (t_nidaq>start) & (t_nidaq<stop)
    visual_stim[cond] = True

# %%

def plot_sample(t0=30, duration=1, 
                channels=range(10,15),
                vshift=1000, 
                subsampling=1,
                figure_scale=2):
    
    fig, ax = pt.figure(ax_scale=figure_scale*np.ones(2))

    ephys_cond = ( t_ephys> t0 ) & ( t_ephys < (t0+duration) )
    
    for i, c in enumerate(rec.get_channel_ids()[channels]):
        v = rec.get_traces(
                        start_frame=np.arange(len(t_ephys))[ephys_cond].min(),
                        end_frame=np.arange(len(t_ephys))[ephys_cond].max()+1,
                        channel_ids=[c])
        ax.plot(t_ephys[ephys_cond][::subsampling], v[::subsampling]+vshift*i,
                color=pt.tab10(i%10))
        pt.annotate(ax, 'chan.%i ' % channels[i], (t_ephys[ephys_cond][0], vshift*i+v[0]), 
                    color=pt.tab10(i%10), xycoords='data', ha='right',fontsize=6)
    ax.axis('off')

    ylim = ax.get_ylim()
    dy, y0 = ylim[1]-ylim[0], ylim[0]
    nidaq_cond = ( t_nidaq> t0 ) & ( t_nidaq < (t0+duration) )
    ax.fill_between(t_nidaq[nidaq_cond][::subsampling], 
                    0*LED[nidaq_cond][::subsampling]+y0, LED[nidaq_cond][::subsampling]*dy+y0,
                    color='blue', alpha=.2, lw=0)
    ax.fill_between(t_nidaq[nidaq_cond][::subsampling], 0*visual_stim[nidaq_cond][::subsampling]+y0, 
                    visual_stim[nidaq_cond][::subsampling]*dy+y0,
                    alpha=.1, lw=0)

    pt.draw_bar_scales(ax, 
                       Xbar=.2, Ybar=200,
                       Xbar_label='200ms', Ybar_label='200uV')
    

plot_sample(t0=70, duration=20, channels=[10,11,13,14])
# %%
plot_sample(t0=9, duration=60, channels=range(120, 140), 
            vshift=2000, subsampling=20)

# %%
si.resample(np.ones(())))