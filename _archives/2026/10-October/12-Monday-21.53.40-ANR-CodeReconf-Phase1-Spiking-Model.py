"""
Copy of `spiking_network_dynamics/demo/PV-SST-VIP.py` for the ANR CodeReconf
project (Phase 1).

The network of `demo/Zerlaut_et_al_2019.py` (Figure 3) with the inhibitory
population RecInh (N=1000) split into PV and SST (N=350 each), and the
disinhibitory population DsInh (N=500) split into VIP and NDNF (N=150
each). The excitatory population RecExc is renamed Pyr.

The splits are fully symmetric: PV and SST have the parameters and
inputs of RecInh, and each projection from RecInh (indegree K) is split into
two projections of indegree K/2 from PV and SST. Same for DsInh split
into VIP and NDNF. Each neuron receives the same synapses as in the
original network, so the population activities are unchanged (PV and
SST rates equal the RecInh rate, VIP and NDNF rates equal the DsInh
rate).

The afferent drive has three 1s phases: a 4Hz oscillation between 2Hz and
8Hz, then (smooth transition) a sustained 6Hz level, then a sustained 15Hz
level (smooth transition). It then goes back (smooth transition) to the 6Hz
level for 3s.

In the last 2s, four stimuli of 300ms spaced by 200ms: two spatio-temporal
patterns (8 events, each recruiting 20 random Pyr neurons) and two
gaussian modulations of the afferent rate (amplitudes 0.5Hz and 1Hz).

    python ANR-CodeReconf-Phase1-Spiking-Model.py         # run, save to data/ANR-CodeReconf-Phase1-Spiking-Model.h5
    python ANR-CodeReconf-Phase1-Spiking-Model.py plot    # plot
"""
import sys, pathlib, os
import numpy as np
from scipy.special import erf
from brian2 import ms, mV, nS, pF, Hz, second

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'spiking_network_dynamics'))  # for `snd`
import snd

# LIF cells, only the threshold differs between populations
LIF = dict(gL=10*nS, C=200*pF, tref=5*ms, EL=-70*mV, Vr=-70*mV)

Model = {
    'dt': 0.1*ms, 'tstop': 6000*ms, 'seed': 3,

    'channels': {'AMPA': dict(kind='exp', E=0*mV, tau=5*ms),
                 'GABA': dict(kind='exp', E=-80*mV, tau=5*ms)},

    'populations': {
        'Pyr': dict(N=4000, kind='LIF', params=dict(LIF, VT=-50*mV)),
        'PV': dict(N=350, kind='LIF', params=dict(LIF, VT=-53*mV)),
        'SST': dict(N=350, kind='LIF', params=dict(LIF, VT=-53*mV)),
        'VIP': dict(N=150, kind='LIF', params=dict(LIF, VT=-50*mV)),
        'NDNF': dict(N=150, kind='LIF', params=dict(LIF, VT=-50*mV)),
    },

    # independent Poisson drive, rate set below
    'afferents': {'AffExc': dict(N=100)},

    # fixed indegree = p*N_pre (connection probability p=0.05 in the original
    # model, p=0.1 and p=0.075 for the afferent drive). Indegrees are kept
    # from the original model (N_RecInh=1000, N_DsInh=500) so that each
    # neuron receives the same input whatever the presynaptic population
    # sizes: the connection probabilities from PV and SST (N=350) are
    # then p=25/350=0.071 and from VIP and NDNF (N=150) p=12.5/150=0.083
    'projections': {
        ('Pyr', 'Pyr'): dict(channel='AMPA', w=2*nS, indegree=200),
        ('Pyr', 'PV'): dict(channel='AMPA', w=2*nS, indegree=200),
        ('Pyr', 'SST'): dict(channel='AMPA', w=2*nS, indegree=200),
        # RecInh -> X (indegree 50) split into PV -> X and SST -> X
        ('PV', 'Pyr'): dict(channel='GABA', w=10*nS, indegree=25),
        ('SST', 'Pyr'): dict(channel='GABA', w=10*nS, indegree=25),
        ('PV', 'PV'): dict(channel='GABA', w=10*nS, indegree=25),
        ('SST', 'PV'): dict(channel='GABA', w=10*nS, indegree=25),
        ('PV', 'SST'): dict(channel='GABA', w=10*nS, indegree=25),
        ('SST', 'SST'): dict(channel='GABA', w=10*nS, indegree=25),
        # DsInh -> X (indegree 25) split into VIP -> X and NDNF -> X
        ('VIP', 'PV'): dict(channel='GABA', w=10*nS, indegree=12.5),
        ('NDNF', 'PV'): dict(channel='GABA', w=10*nS, indegree=12.5),
        ('VIP', 'SST'): dict(channel='GABA', w=10*nS, indegree=12.5),
        ('NDNF', 'SST'): dict(channel='GABA', w=10*nS, indegree=12.5),
        ('AffExc', 'Pyr'): dict(channel='AMPA', w=4*nS, indegree=10),
        ('AffExc', 'PV'): dict(channel='AMPA', w=4*nS, indegree=10),
        ('AffExc', 'SST'): dict(channel='AMPA', w=4*nS, indegree=10),
        ('AffExc', 'VIP'): dict(channel='AMPA', w=4*nS, indegree=7.5),
        ('AffExc', 'NDNF'): dict(channel='AMPA', w=4*nS, indegree=7.5),
    },

    'record': {pop: dict(spikes=True, rate=True, variables=['V'], record=10)
               for pop in ['Pyr', 'PV', 'SST', 'VIP', 'NDNF']},
}

# release probability per synaptic channel, with connectivities (indegrees
# above) scaled by 1/P_RELEASE so that the mean synaptic input is unchanged
P_RELEASE = {'AMPA': 0.5, 'GABA': 0.5}
# then, connectivity of the recurrent excitation (E->E and E->I) scaled by
EXC_CONNECTIVITY_FACTOR = 0.5
for (pre, post), proj in Model['projections'].items():
    proj['p_release'] = P_RELEASE[proj['channel']]
    proj['indegree'] = round(proj['indegree']/proj['p_release'], 6)
    if pre == 'Pyr':
        proj['indegree'] = round(EXC_CONNECTIVITY_FACTOR*proj['indegree'], 6)


def waveform(t, freq=4*Hz, low=0*Hz, high=10*Hz, 
             level2=6*Hz, level3=17*Hz,
             T=1000*ms, rise=50*ms):
    """ afferent rate: three phases of duration T, then a fourth phase
        1) oscillation at `freq` between `low` and `high` (starts at `low`)
        2) sustained `level2`
        3) sustained `level3`
        4) back to `level2` (from 3T until the end)
        with smooth transitions (width `rise`) between phases """
    osc = (low+high)/2-(high-low)/2*np.cos(2*np.pi*freq*t)
    s2 = (1+erf((t-T)/rise))/2    # smooth switch from phase 1 to phase 2
    s3 = (1+erf((t-2*T)/rise))/2  # smooth switch from phase 2 to phase 3
    s4 = (1+erf((t-3*T)/rise))/2  # smooth switch from phase 3 to phase 4
    return osc*(1-s2)+level2*s2*(1-s3)+level3*s3*(1-s4)+level2*s4


t = np.arange(int(Model['tstop']/Model['dt']))*Model['dt']
Model['afferents']['AffExc']['rate'] = waveform(t)

# ---- stimuli in the last 2s: four stimuli of 300ms spaced by 200ms
#   stim 1 & 2: two spatio-temporal patterns (explicit spikes), each made of
#               nEvents events (random times) recruiting nNeurons random
#               Pyr neurons (one synapse of weight PATTERN_W per neuron)
#   stim 3 & 4: gaussian modulation of the afferent rate, amplitude A
STIM_DURATION, STIM_INTERVAL = 300*ms, 400*ms
STIM_ONSETS = Model['tstop']-2500*ms+np.arange(4)*(STIM_DURATION+STIM_INTERVAL)
nEvents, nNeurons, PATTERN_W = 6, 200, 15*nS
GAUSSIAN_AMPLITUDES, GAUSSIAN_SIGMA = [2*Hz, 4*Hz], STIM_DURATION/6

rng = np.random.default_rng(Model['seed'])
indices, times, i, j = [], [], [], []
for p, onset in enumerate(STIM_ONSETS[:2]):
    tevents = np.sort(rng.uniform(0, float(STIM_DURATION/Model['dt']), nEvents))
    for e, te in enumerate(tevents):
        indices.append(p*nEvents+e)  # one source per event, firing once
        times.append(float((onset+np.round(te)*Model['dt'])/ms))
        i += [p*nEvents+e]*nNeurons
        j += list(rng.choice(Model['populations']['Pyr']['N'], nNeurons,
                             replace=False))
Model['afferents']['Patterns'] = dict(N=2*nEvents, indices=np.array(indices),
                                      times=np.array(times)*ms)
Model['projections'][('Patterns', 'Pyr')] = dict(channel='AMPA', w=PATTERN_W,
                                                    i=np.array(i), j=np.array(j))
Model['record']['Patterns'] = dict(spikes=True)

for onset, A in zip(STIM_ONSETS[2:], GAUSSIAN_AMPLITUDES):
    tc = onset+STIM_DURATION/2
    Model['afferents']['AffExc']['rate'] += A*np.exp(-(t-tc)**2/2/GAUSSIAN_SIGMA**2)

DATA_FILE = str(ROOT/'data'/'ANR-CodeReconf-Phase1-Spiking-Model.h5')

POPS = [('Pyr', '#008080'), ('PV', 'tab:red'),
        ('SST', 'tab:orange'), ('VIP', 'tab:purple'),
        ('NDNF', 'goldenrod')] 


if sys.argv[-1] == 'plot':

    import matplotlib.pyplot as plt
    from scipy.ndimage import gaussian_filter1d

    data = snd.io.load(DATA_FILE)
    # one figure, panels from top to bottom with their relative height
    # (0: panel not shown)
    PANELS = {'Vm': 5,   # mean Vm of Pyr
            #   'mean_Vm': 1,        # single-cell Vms
            #   'rate': 1,      # population rates
              'raster': 2,    # raster plot
              'aff_rate': 1}  # afferent rate

    FIGSIZE = (15, 7)  # (width, height) in cm
    # time scale bar, on the mean Vm panel (or on the Vm panel if not shown)
    TBAR = 100*ms

    shown = [k for k, size in PANELS.items() if size]
    fig, AX = plt.subplots(len(shown), 1, figsize=[x/2.54 for x in FIGSIZE], sharex=True,
                           squeeze=False,
                           gridspec_kw=dict(height_ratios=[PANELS[k] for k in shown]))
    plt.subplots_adjust(hspace=0.)
    AX = dict(zip(shown, AX[:, 0]))

    # 1) mean +/- s.e.m. of V over all recorded Pyr cells
    if 'mean_Vm' in AX:
        state = data['Pyr_state']
        V = np.asarray(state['V']/mV)
        mean= gaussian_filter1d(V.mean(axis=0), 60)
        # sem = gaussian_filter1d(V.std(axis=0)/np.sqrt(len(V)), 60)
        sem = gaussian_filter1d(V.std(axis=0), 60)
        AX['mean_Vm'].fill_between(state['t']/ms, mean-sem, mean+sem,
                                   color='#008080', alpha=0.3, lw=0)
        AX['mean_Vm'].plot(state['t']/ms, mean, color='#008080', lw=1)
        snd.plot.scale_bars(AX['mean_Vm'], Vbar=5*mV, Tbar=TBAR)

    # 2) membrane potentials: 3 Pyr cells and 1 cell of each Inh population
    if 'Vm' in AX:
        traces = [('Pyr', k, '#008080') for k in range(3)]+\
                 [(pop, 0, c) for pop, c in POPS[1:]]
        snd.plot.stacked_membrane_potentials(data, AX['Vm'], traces,
                                             shift=30*mV,
                                             spike_peak=-40*mV, spike_style='--',
                                            #  clip=2*ms,
                                             lw=0.5, Vbar=20*mV,
                                             Tbar=None if 'mean_Vm' in AX else TBAR,
                                             bar_loc='top left')

    # 3) population rates
    if 'rate' in AX:
        for pop, c in POPS[1:]+POPS[:1]:  # Pyr last (on top)
            r = data['%s_rate' % pop]
            kernel = np.ones(200)/200  # 20ms smoothing
            AX['rate'].semilogy(r['t']/ms, 0.05+np.convolve(r['rate']/Hz, kernel, 'same'),
                                color=c, label=pop, lw=1 if pop == 'Pyr' else 0.5)
        AX['rate'].set_ylabel('rate (Hz)')
        AX['rate'].set_ylim(0.1, 50)
        AX['rate'].set_yticks([0.1, 1, 10], ['0.1', '1', '10'])
        for side in ['top', 'right']:
            AX['rate'].spines[side].set_visible(False)

    # 4) raster: 1 neuron over RASTER_SUBSAMPLING, and spikes picked in random
    # order, each removing the spikes of the same neuron within the dead time
    if 'raster' in AX:
        RASTER_SUBSAMPLING = 4
        offset = 0
        for pop, c in POPS:
            sp = data['%s_spikes' % pop]
            keep = snd.plot.thin_spikes(sp['i'], sp['t'], dead_time=1000*ms,
                                        random=True, seed=Model['seed'],
                                        subsampling=RASTER_SUBSAMPLING)
            AX['raster'].plot(sp['t'][keep]/ms,
                              sp['i'][keep]//RASTER_SUBSAMPLING+offset,
                              'o', color=c, ms=1, mew=0)  # plain dots
            offset += int(np.ceil(sp['N']/RASTER_SUBSAMPLING))
        for side in ['left', 'top', 'right']:
            AX['raster'].spines[side].set_visible(False)
        AX['raster'].set_yticks([])

    # 5) afferent rate
    if 'aff_rate' in AX:
        rate = data['model']['afferents']['AffExc']['rate']
        AX['aff_rate'].plot(t/ms, rate/Hz, 'k')
        AX['aff_rate'].annotate(' aff. rate', (t[-1]/ms, np.median(rate/Hz)),
                                va='center', annotation_clip=False)
        snd.plot.scale_bars(AX['aff_rate'], Vbar=2*Hz, Vunit=Hz)

    # no time axis (the time scale bar is the time reference), no y-axis
    # except for the rates
    for ax in AX.values():
        ax.set_xlabel('')
        ax.spines['bottom'].set_visible(False)
        ax.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
    plt.show()
    fig.savefig(os.path.join(os.path.expanduser('~'), 'OneDrive - ICM', 'Lab-Notebook', 'Grants', '2027-ANR-CodeReconf', 'sim.svg'))

else:

    net, data = snd.run(Model, filename=DATA_FILE, report='text')
    snd.describe(net)
    print()
    print(' --- simulations results ---')
    for pop, _ in POPS:
        sp = data['%s_spikes' % pop]
        print('%s: %.2f Hz' % (pop, len(sp['t'])/sp['N']/float(Model['tstop']/second)))
    print('--> Run "python ANR-CodeReconf-Phase1-Spiking-Model.py plot" to plot the results')
