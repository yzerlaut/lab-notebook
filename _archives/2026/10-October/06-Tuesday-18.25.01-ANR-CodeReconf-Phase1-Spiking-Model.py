"""
Copy of `spiking_network_dynamics/demo/PV-SST-VIP.py` for the ANR CodeReconf
project (Phase 1).

The network of `demo/Zerlaut_et_al_2019.py` (Figure 3) with the inhibitory
population RecInh split into two halves, PvInh and SstInh, and DsInh
renamed VipInh.

The split is fully symmetric: PvInh and SstInh have the parameters and inputs
of RecInh, and each projection from RecInh (indegree K) is split into two
projections of indegree K/2 from PvInh and SstInh. Each neuron receives the
same synapses as in the original network, so the dynamics are unchanged
(PvInh and SstInh rates equal the RecInh rate).

The afferent drive has three 1s phases: a 4Hz oscillation between 2Hz and
8Hz, then (smooth transition) a sustained 6Hz level, then a sustained 15Hz
level (smooth transition). It then goes back (smooth transition) to the 6Hz
level for 3s.

    python ANR-CodeReconf-Phase1-Spiking-Model.py         # run, save to data/ANR-CodeReconf-Phase1-Spiking-Model.h5
    python ANR-CodeReconf-Phase1-Spiking-Model.py plot    # plot
"""
import sys, pathlib
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
        'RecExc': dict(N=4000, kind='LIF', params=dict(LIF, VT=-50*mV)),
        'PvInh': dict(N=500, kind='LIF', params=dict(LIF, VT=-53*mV)),
        'SstInh': dict(N=500, kind='LIF', params=dict(LIF, VT=-53*mV)),
        'VipInh': dict(N=500, kind='LIF', params=dict(LIF, VT=-50*mV)),
    },

    # independent Poisson drive, rate set below
    'afferents': {'AffExc': dict(N=100)},

    # fixed indegree = p*N_pre (connection probability p=0.05 in the original
    # model, p=0.1 and p=0.075 for the afferent drive)
    'projections': {
        ('RecExc', 'RecExc'): dict(channel='AMPA', w=2*nS, indegree=200),
        ('RecExc', 'PvInh'): dict(channel='AMPA', w=2*nS, indegree=200),
        ('RecExc', 'SstInh'): dict(channel='AMPA', w=2*nS, indegree=200),
        # RecInh -> X (indegree 50) split into PvInh -> X and SstInh -> X
        ('PvInh', 'RecExc'): dict(channel='GABA', w=10*nS, indegree=25),
        ('SstInh', 'RecExc'): dict(channel='GABA', w=10*nS, indegree=25),
        ('PvInh', 'PvInh'): dict(channel='GABA', w=10*nS, indegree=25),
        ('SstInh', 'PvInh'): dict(channel='GABA', w=10*nS, indegree=25),
        ('PvInh', 'SstInh'): dict(channel='GABA', w=10*nS, indegree=25),
        ('SstInh', 'SstInh'): dict(channel='GABA', w=10*nS, indegree=25),
        ('VipInh', 'PvInh'): dict(channel='GABA', w=10*nS, indegree=25),
        ('VipInh', 'SstInh'): dict(channel='GABA', w=10*nS, indegree=25),
        ('AffExc', 'RecExc'): dict(channel='AMPA', w=4*nS, indegree=10),
        ('AffExc', 'PvInh'): dict(channel='AMPA', w=4*nS, indegree=10),
        ('AffExc', 'SstInh'): dict(channel='AMPA', w=4*nS, indegree=10),
        ('AffExc', 'VipInh'): dict(channel='AMPA', w=4*nS, indegree=7.5),
    },

    'record': {pop: dict(spikes=True, rate=True, variables=['V'], record=4)
               for pop in ['RecExc', 'PvInh', 'SstInh', 'VipInh']},
}

# release probability per synaptic channel, with connectivities (indegrees
# above) scaled by 1/P_RELEASE so that the mean synaptic input is unchanged
P_RELEASE = {'AMPA': 0.5, 'GABA': 0.5}
# then, connectivity of the recurrent excitation (E->E and E->I) scaled by
EXC_CONNECTIVITY_FACTOR = 0.5
for (pre, post), proj in Model['projections'].items():
    proj['p_release'] = P_RELEASE[proj['channel']]
    proj['indegree'] = round(proj['indegree']/proj['p_release'], 6)
    if pre == 'RecExc':
        proj['indegree'] = round(EXC_CONNECTIVITY_FACTOR*proj['indegree'], 6)


def waveform(t, freq=4*Hz, low=0*Hz, high=8*Hz, 
             level2=6*Hz, level3=15*Hz,
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

DATA_FILE = str(ROOT/'data'/'ANR-CodeReconf-Phase1-Spiking-Model.h5')

POPS = [('RecExc', 'tab:green'), ('PvInh', 'tab:red'),
        ('SstInh', 'tab:orange'), ('VipInh', 'tab:purple')]


if sys.argv[-1] == 'plot':

    import matplotlib.pyplot as plt
    data = snd.io.load(DATA_FILE)
    fig, AX = plt.subplots(6, 1, figsize=(7, 9), sharex=True,
                           gridspec_kw=dict(height_ratios=[1, 3, 2, 1, 1, 1]))
    rate = data['model']['afferents']['AffExc']['rate']
    AX[0].plot(t/ms, rate/Hz, 'k')
    AX[0].set_ylabel('aff. rate\n(Hz)')
    offset = 0
    for pop, c in POPS:
        sp = data['%s_spikes' % pop]
        AX[1].plot(sp['t']/ms, sp['i']+offset, '.', color=c, ms=0.5)
        offset += sp['N']
        r = data['%s_rate' % pop]
        kernel = np.ones(100)/100  # 10ms smoothing
        AX[2].plot(r['t']/ms, np.convolve(r['rate']/Hz, kernel, 'same'),
                   color=c, label=pop)
    AX[1].set_ylabel('neuron')
    AX[2].set_ylabel('rate (Hz)')
    AX[2].legend(frameon=False, fontsize='small')
    for ax, pop in zip(AX[3:], ['RecExc', 'PvInh', 'SstInh']):
        state = data['%s_state' % pop]
        ax.plot(state['t']/ms, state['V'][0]/mV, color=dict(POPS)[pop])
        ax.set_ylabel('%s\nV (mV)' % pop)
    AX[-1].set_xlabel('time (ms)')
    plt.show()

else:

    net, data = snd.run(Model, filename=DATA_FILE, report='text')
    snd.describe(net)
    print()
    print(' --- simulations results ---')
    for pop, _ in POPS:
        sp = data['%s_spikes' % pop]
        print('%s: %.2f Hz' % (pop, len(sp['t'])/sp['N']/float(Model['tstop']/second)))
    print('--> Run "python ANR-CodeReconf-Phase1-Spiking-Model.py plot" to plot the results')
