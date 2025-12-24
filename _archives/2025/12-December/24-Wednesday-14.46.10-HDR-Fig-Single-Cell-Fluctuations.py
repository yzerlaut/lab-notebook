# %%
import sys
sys.path += ['./neural_network_dynamics']

import numpy as np
import brian2
from ntwk.cells.cell_construct import get_membrane_equation

import plot_tools as pt

# %%

FS_params = {
    'N':1, 'Gl':7., 'Cm':200.,'Trefrac':5.,
    'El':-65., 'Vthre':-55., 'Vreset':-65., 'deltaV':0.,
    'a':0., 'b': 0., 'tauw':1e9
}

RS_params = {
    'N':1, 'Gl':5., 'Cm':200.,'Trefrac':5.,
    'El':-65., 'Vthre':-55., 'Vreset':-65., 'deltaV':0.,
    'a':5., 'b': 70., 'tauw':200

}

# %%
def step_sim(params,
             amps=[0,160,0,-190,0,270,0],
             durations=[200,450,400,400,400,600,50]
             ):

    # initialize
    net = brian2.Network()

    eqs = """
    dV/dt = (%(Gl)f*nS*(%(El)f*mV - V) + %(Gl)f*nS*%(deltaV)f*mV*exp(-(%(Vthre)f*mV-V)/(%(deltaV)f*mV)) + I - w_adapt)/(%(Cm)f*pF) : volt (unless refractory) 
    dw_adapt/dt = ( -%(a)f*nS*( %(El)f*mV - V) - w_adapt )/(%(tauw)f*ms) : amp  
    I = I0 : amp
    I0 : amp
    """ % params
    neurons = brian2.NeuronGroup(params['N'], model=eqs,
               method='euler', refractory=str(params['Trefrac'])+'*ms',
               threshold='V>'+str(params['Vthre']+5.*params['deltaV'])+'*mV',
               reset='V='+str(params['Vreset'])+'*mV; w_adapt+='+str(params['b'])+'*pA')
    neurons.V = params['El']*brian2.mV
    net.add(neurons)

    trace = brian2.StateMonitor(neurons, 'V', record=0)
    net.add(trace)
    spikes = brian2.SpikeMonitor(neurons)
    net.add(spikes)

    I, ilast = np.zeros(len(trace.t)), len(trace.t)

    for amp, d in zip(amps, durations):

        neurons.I0 = amp*brian2.pA
        net.run(d * brian2.ms)

        # update I trace
        I = np.concatenate([I, amp*np.ones(len(trace.t)-ilast)])
        ilast = len(trace.t)

    return trace.t / brian2.ms,\
           trace[0].V[:] / brian2.mV, I, spikes.t / brian2.ms

# %%

def show_spikes(t, Vm, spikes,
                peak=10):
    for s in spikes:
        i = np.argmin((t-s)**2)
        Vm[i] = peak 

fig, AX = pt.figure(hspace=0.1, ax_scale=(2.5,0.8),
                    axes_extents=[[[1,5]],[[1,1]]])
for i, params in enumerate([FS_params, RS_params]):
    t, Vm, I, spikes = step_sim(params)
    show_spikes(t, Vm, spikes)
    pt.plot(t, Vm+i*100, ax=AX[0])

for ax in pt.flatten(AX):
    ax.axis('off')
AX[1].plot(t, 0*t, ':')
pt.plot(t, I, ax=AX[1])
pt.draw_bar_scales(AX[0], 
                   Ybar=20, Ybar_label='20mV',
                   Xbar=100, Xbar_label='100ms')
pt.draw_bar_scales(AX[1], Xbar=1e-6, Ybar=200, Ybar_label='200pA ')

# %%

def OrnsteinUhlenbeck_Process(mu, sigma, tau, dt=0.1, tstop=100, seed=1):
    np.random.seed(seed)
    diffcoef = 2*sigma**2/tau
    y0 = mu
    n_steps = int(tstop/dt)
    A = np.sqrt(diffcoef*tau/2.*(1-np.exp(-2*dt/tau)))
    noise = np.random.randn(n_steps)
    y = np.zeros(n_steps)
    y[0] = y0
    for i in range(n_steps-1):
        y[i+1] = y0 + (y[i]-y0)*np.exp(-dt/tau)+A*noise[i]
    return y

def noisy_sim(params,
              mu=100, sigma=200, tau=0.1, seed=1,
              tstop=.1):

    # initialize
    net = brian2.Network()
    eqs = """
    dV/dt = (%(Gl)f*nS*(%(El)f*mV - V) + %(Gl)f*nS*%(deltaV)f*mV*exp(-(%(Vthre)f*mV-V)/(%(deltaV)f*mV)) + I - w_adapt)/(%(Cm)f*pF) : volt (unless refractory) 
    dw_adapt/dt = ( -%(a)f*nS*( %(El)f*mV - V) - w_adapt )/(%(tauw)f*ms) : amp  
    I = stimulus(t)*I0 : amp
    I0 : amp
    """ % params
    neurons = brian2.NeuronGroup(params['N'], model=eqs,
               method='euler', refractory=str(params['Trefrac'])+'*ms',
               threshold='V>'+str(params['Vthre']+5.*params['deltaV'])+'*mV',
               reset='V='+str(params['Vreset'])+'*mV; w_adapt+='+str(params['b'])+'*pA')
    neurons.V = params['El']*brian2.mV
    neurons.I0 = 1*brian2.pA
    net.add(neurons)
    I = OrnsteinUhlenbeck_Process(0, 1, tau,
                                  dt=brian2.defaultclock.dt/brian2.second,
                                  tstop=tstop, seed=seed)
    tt = np.arange(len(I))*brian2.defaultclock.dt/brian2.second
    for t0 in [0.15, 0.45, 0.92, 1.5, 2.4, 2.42, 3.2]:
        I += 2.*np.exp(-(tt-t0)**2/2./0.01**2)
    I = mu+sigma*I
    stimulus = brian2.TimedArray(I, dt=brian2.defaultclock.dt)

    trace = brian2.StateMonitor(neurons, 'V', record=0)
    net.add(trace)
    spikes = brian2.SpikeMonitor(neurons)
    net.add(spikes)

    net.run(tstop*brian2.second)

    return trace.t / brian2.ms,\
        trace[0].V[:] / brian2.mV, I, spikes.t / brian2.ms

fig, AX = pt.figure(hspace=0., ax_scale=(2.5,0.8),
                    axes_extents=[[[1,5]],[[1,1]]])
for i, params in enumerate([FS_params, RS_params]):
    t, Vm, I, spikes = noisy_sim(params,
                                 mu=-40, sigma=60, tau=0.1,
                                 tstop=3.4, seed=1)
    show_spikes(t, Vm, spikes)
    pt.plot(t, Vm+i*100, ax=AX[0])

for ax in pt.flatten(AX):
    ax.axis('off')
AX[1].plot(t, 0*t, ':')
pt.plot(t, I, ax=AX[1])
pt.draw_bar_scales(AX[0], 
                   Ybar=20, Ybar_label='20mV',
                   Xbar=100, Xbar_label='100ms')
pt.draw_bar_scales(AX[1], Xbar=1e-6, Ybar=100, Ybar_label='100pA ')

# %%
FS1_params = {
    'N':1, 'Gl':7., 'Cm':200.,'Trefrac':5.,
    'El':-65., 'Vthre':-54., 'Vreset':-65., 'deltaV':0.,
    'a':0., 'b': 0., 'tauw':1e9
}

FS2_params = {
    'N':1, 'Gl':7., 'Cm':200.,'Trefrac':5.,
    'El':-65., 'Vthre':-57., 'Vreset':-65., 'deltaV':2.,
    'a':0., 'b': 0., 'tauw':200

}

fig, AX = pt.figure(hspace=0.1, ax_scale=(2.5,0.8),
                    axes_extents=[[[1,5]],[[1,1]]])
for i, params in enumerate([FS1_params, FS2_params]):
    t, Vm, I, spikes = step_sim(params)
    show_spikes(t, Vm, spikes)
    pt.plot(t, Vm+i*100, ax=AX[0])

for ax in pt.flatten(AX):
    ax.axis('off')
AX[1].plot(t, 0*t, ':')
pt.plot(t, I, ax=AX[1])
pt.draw_bar_scales(AX[0], 
                   Ybar=20, Ybar_label='20mV',
                   Xbar=100, Xbar_label='100ms')
pt.draw_bar_scales(AX[1], Xbar=1e-6, Ybar=200, Ybar_label='200pA ')

# %%

fig, AX = pt.figure(hspace=0., ax_scale=(2.5,0.8),
                    axes_extents=[[[1,5]],[[1,1]]])
for i, params in enumerate([FS1_params, FS2_params]):
    t, Vm, I, spikes = noisy_sim(params,
                                 mu=-50, sigma=60, tau=0.1,
                                 tstop=3.4, seed=1)
    show_spikes(t, Vm, spikes)
    pt.plot(t, Vm+i*100, ax=AX[0])

for ax in pt.flatten(AX):
    ax.axis('off')
AX[1].plot(t, 0*t, ':')
pt.plot(t, I, ax=AX[1])
pt.draw_bar_scales(AX[0], 
                   Ybar=20, Ybar_label='20mV',
                   Xbar=100, Xbar_label='100ms')
pt.draw_bar_scales(AX[1], Xbar=1e-6, Ybar=100, Ybar_label='100pA ')

# %%
def Print(params):
    return """
    $g_L$=%(Gl).1fnS
    $V_{thre}$=%(Vthre).1fmV 
    $\delta_V$=%(deltaV).1fmV
    $a$=%(a).1fnS
    $b$=%(b).1fpA
    """ % params

FS1_params = {
    'N':1, 'Gl':7., 'Cm':200.,'Trefrac':5.,
    'El':-65., 'Vthre':-54., 'Vreset':-65., 'deltaV':0.,
    'a':0., 'b': 0., 'tauw':1e9
}
# %%
