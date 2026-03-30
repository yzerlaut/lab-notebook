# %%
import sys, os
import numpy as np

# %%
# --- SINGLE CELL SIMULATIONS
if True:

    sys.path += ['./']
    import plot_tools as pt

    fig, ax = pt.figure(ax_scale=(1.5,1.3))

    dt, tstop = 0.1, 550
    t = np.arange(int(tstop/dt))*dt

    def doubleExp_waveform(t, t0, Vm, T1=2, T2=20, w=1.):

        cond = t>t0
        Vm[cond] = Vm[cond] + w*\
            (np.exp(-(t[cond]-t0)/T2)-np.exp(-(t[cond]-t0)/T1))

    vS, vD = 0*t, 0*t
    np.random.seed(10)
    events = np.cumsum(np.random.exponential(10, size=6))
    t0 = 10
    for e in events:
        doubleExp_waveform(t, e+t0, vD, 1, 15, 3.)
        doubleExp_waveform(t, e+t0, vS, 4, 20, 1.)

    e = 170
    doubleExp_waveform(t, e, vD, 20, 40, 10.)
    doubleExp_waveform(t, e, vS, 25, 50, 7.)

    t0 = 400
    for e in events:
        doubleExp_waveform(t, e+t0, vD, 1, 15, 3.)
        doubleExp_waveform(t, e+t0, vS, 4, 20, 1.)
    e = t0
    doubleExp_waveform(t, e, vD, 20, 40, 10.)
    doubleExp_waveform(t, e, vS, 25, 50, 7.)

    ax.plot(t, vS, color='tab:grey')
    ax.plot(t, 5+vD, color='tab:red')
    ax.axis('off')
    pt.draw_bar_scales(ax, Xbar=50, Xbar_label='50ms',
                       Ybar=3, Ybar_label='5mV')
    pt.save(fig)
    pt.plt.show()


# %%
# --- GRAPH SINGLE PATTERNS
if False:

    sys.path += ['./']
    import plot_tools as pt

    fig, AX = pt.figure(axes=(3,2), wspace=0.6,
                        hspace=0.3, ax_scale=(.85,0.6))

    dt = 0.1
    tstop = 100

    sys.path += ['./neural_network_dynamics']
    import ntwk
    from ntwk.stim.poisson_generator import spikes_from_time_varying_rate

    tF = np.arange(int(tstop/dt))*dt
    tB0, sB = spikes_from_time_varying_rate(tF, 2+0*tF, 
                                       N=100, SEED=3)
    tFV = np.arange(int((tstop+30)/dt))*dt
    for i in range(3):
        tB = tB0+np.random.randn(len(sB))*2.
        tV, sV = spikes_from_time_varying_rate(tFV, .3+0*tFV, 
                                        N=100, SEED=26+i)
        tV -= 20
        AX[0][i].plot(list(tB)+list(tV), list(sB)+list(sV), 'o', ms=1., color='#008080')

    tB0, sB = spikes_from_time_varying_rate(tF, 6+0*tF, 
                                       N=100, SEED=3)
    tFV = np.arange(int((tstop+30)/dt))*dt
    for i in range(3):
        tB = tB0+np.random.randn(len(sB))*5.
        tV, sV = spikes_from_time_varying_rate(tFV, 2+0*tFV, 
                                        N=100, SEED=26+i)
        tV -= 20
        AX[1][i].plot(list(tB)+list(tV), list(sB)+list(sV), 'o', ms=1., color='#008080')


    # AX[0][1].plot(list(BASE[0])+list(VAR[0]), list(BASE[1])+list(VAR[1]), 'o', ms=1., color='#008080')
    # AX[0][0].plot(P1[0], P1[1], 'o', ms=1., color='#008080')
    # ax.bar([1.5], [0.11], yerr=[0.03], color='tab:olive')

    # pt.set_plot(ax, 
    #             ylabel='cross-correlation\n(trial-to-trial)',
    #             xticks=[0,1.5], xticks_labels=[])
    for ax in pt.flatten(AX):
        pt.set_plot(ax, xticks=[0, 50, 100], yticks=[],
                    xticks_labels=[] if ax in AX[0] else None,
                    ylabel='neurons' if ax==AX[0][0] else '',
                    xlabel='time from stim. (ms)' if ax==AX[1][1] else '',
                    xlim=[-20,110], ylim=[-10,110])
    for i, ax in enumerate(AX[0]):
        ax.set_title('trial #%i' % (i+1))
    for i, ax in enumerate(AX[0]):
        ax.fill_between([0,100], [-5,-5], [105,105], color='tab:blue', alpha=.2, lw=0)
    for i, ax in enumerate(AX[1]):
        ax.fill_between([0,100], [-5,-5], [105,105], color='tab:olive', alpha=.2, lw=0)

    pt.plt.show()
    pt.save(fig)

# --- GRAPH RELIABILITY RESPONSE
if False:

    sys.path += ['./']
    import plot_tools as pt
    fig, ax = pt.figure(ax_scale=(0.95,1.))

    ax.bar([0], [0.32], yerr=[0.13], color='tab:blue')
    ax.bar([1.5], [0.11], yerr=[0.03], color='tab:olive')

    pt.set_plot(ax, 
                ylabel='cross-correlation\n(trial-to-trial)',
                xticks=[0,1.5], xticks_labels=[])
    pt.plt.show()
    pt.save(fig)

# %%
# --- GRAPH AMPLITUDE RESPONSE
if False:

    sys.path += ['./']
    import plot_tools as pt
    fig, ax = pt.figure(ax_scale=(0.95,.9))

    ax.bar([0], [5], yerr=[2], color='tab:blue')
    ax.bar([1.5], [15.3], yerr=[4.2], color='tab:olive')

    pt.set_plot(ax, 
                ylabel='rate (Hz)',
                xticks=[0,1.5], xticks_labels=[])
    pt.save(fig)

# %%
# --- NETWORK SIMULATION CLASSICAL DISINHIBITION CASE --- #
if False:
    import matplotlib.pylab as plt

    # sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
    sys.path += ['./neural_network_dynamics']
    import ntwk

    ################################################################
    ## ------ Construct populations with their equations -------- ##
    ## ------------- with recurrent connections ----------------- ##
    ################################################################
    N=10
    Model = {
        'N_PyrExc':4*N, 'N_PvInh':1*N, 'N_SstInh':1*N, 'N_VipInh':1*N, 
        'N_AffExc':500, 'N_AffInh':100,
        # synaptic time constants
        'Tsyn_Exc':5., 'Tsyn_Inh':5.,
        # synaptic reversal potentials
        'Erev_Exc':0., 'Erev_Inh': -80.,
        # simulation parameters
        'dt':0.1, 'tstop': 1500., 'SEED':3, # low by default, see later
    }
    POPS = ['PyrExc', 'PvInh', 'VipInh', 'SstInh']
    for key in POPS:
        Model['Q_AffExc_%s' % key] = 1.
        Model['Q_AffInh_%s' % key] = 5.

        Model['p_AffExc_%s' % key] = 0.04
        Model['p_AffInh_%s' % key] = 0.04

        Model[key+'_Gl'] = 10.
        Model[key+'_Cm'] = 200.
        Model[key+'_Trefrac'] = 3.
        Model[key+'_El'] = -60.
        Model[key+'_Vthre'] = -50.
        Model[key+'_Vreset'] = -60.
        Model[key+'_deltaV'] = 1.
        Model[key+'_a'] = 0.
        Model[key+'_b'] =  0.
        Model[key+'_tauw'] = 1e9

    # %%

    NTWK = ntwk.build.populations(Model, POPS,
                                    AFFERENT_POPULATIONS=['AffExc', 'AffInh'],
                                    with_raster=True,
                                    with_Vm=[4,1,1,1,1],
                                    verbose=True)

    #######################################
    ########### AFFERENT INPUTS ###########
    #######################################

    t_array = ntwk.arange(int(Model['tstop']/Model['dt']))*Model['dt']

    for key in POPS:
        Model['Fexc_%s' % key] = 350.+0.*t_array
        Model['Finh_%s' % key] = 700.+0.*t_array

    stim_cond = (t_array>600) & (t_array<650)

    Model['Fexc_PyrExc'][stim_cond] += 80
    Model['Fexc_PvInh'][stim_cond] += 30
    Model['Fexc_SstInh'][stim_cond] += 50

    context_cond = (t_array>900) & (t_array<1050)

    Model['Fexc_PyrExc'][context_cond] += 50.
    Model['Fexc_PvInh'][context_cond] += 40.
    Model['Fexc_VipInh'][context_cond] += 100.
    Model['Fexc_SstInh'][context_cond] -= 50.

    stim_and_context_cond = (t_array>1300) & (t_array<1380)

    Model['Fexc_PyrExc'][stim_and_context_cond] += 110.
    Model['Fexc_PvInh'][stim_and_context_cond] += 40.
    Model['Fexc_VipInh'][stim_and_context_cond] += 100.
    Model['Fexc_SstInh'][stim_and_context_cond] -= 50.

    Model['Fexc_SstInh'][~context_cond & ~stim_and_context_cond] += 50.

    # # # afferent excitation onto cortical excitation and inhibition
    for i, tpop in enumerate(POPS):
        ntwk.stim.construct_feedforward_input(NTWK, tpop, 'AffExc',
                                                t_array, Model['Fexc_%s' % tpop],
                                                verbose=True,
                                                SEED=10*(i+1))
        ntwk.stim.construct_feedforward_input(NTWK, tpop, 'AffInh',
                                                t_array, Model['Finh_%s' % tpop],
                                                verbose=True,
                                                SEED=2*(i+1))

    ################################################################
    ## --------------- Initial Condition ------------------------ ##
    ################################################################
    ntwk.build.initialize_to_rest(NTWK)

    #####################
    ## ----- Run ----- ##
    #####################
    network_sim = ntwk.collect_and_run(NTWK, verbose=True)

    ntwk.recording.write_as_hdf5(NTWK, filename='classical-dsnh.h5')


    # %%
    # ######################
    # ## ----- Plot ----- ##
    # ######################

    COLORS = ['#008080', '#d40000', '#800080','#ff6600']

    ## load file
    model = 'classical-dsnh'

    data = ntwk.recording.load_dict_from_hdf5(\
                                        '%s.h5' % model)

    fig, AX = ntwk.plots.pretty(data, 
                            COLORS=COLORS,
                    axes_extents = dict(Raster=1, Vm=3),
                    Raster_args=dict(ms=1.5, with_annot=False, subsampling=2),
                    Vm_args=dict(subsampling=1, lw=0.6, shift=40.,
                                clip_spikes=False, vpeak=0),
            fig_args=dict(ax_scale=(2.3, 1.3), dpi=150,
                            hspace=0.1, bottom=0.2, top=0.2, 
                            left=0.1, right = 0.1))
    plt.show()
    

# %%
# --- NETWORK SIMULATION CLASSICAL VS UPDATED CASE --- #
if False:
    import sys, os
    import numpy as np
    import matplotlib.pylab as plt

    # sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
    sys.path += ['./neural_network_dynamics']
    import ntwk

    ################################################################
    ## ------ Construct populations with their equations -------- ##
    ## ------------- with recurrent connections ----------------- ##
    ################################################################
    N=3
    Model = {
        'N_PyrExc':4*N, 'N_PvInh':1*N, 'N_SstInh':1*N, 'N_VipInh':1*N, 'N_ChInh':1*N,
        'N_AffExc':500, 'N_AffInh':100,
        # synaptic time constants
        'Tsyn_Exc':5., 'Tsyn_Inh':5.,
        # synaptic reversal potentials
        'Erev_Exc':0., 'Erev_Inh': -80.,
        # simulation parameters
        'dt':0.1, 'tstop': 1500., 'SEED':3, # low by default, see later
    }
    POPS = ['PyrExc', 'PvInh', 'VipInh', 'SstInh', 'ChInh']
    for key in POPS:
        Model['Q_AffExc_%s' % key] = 1.
        Model['Q_AffInh_%s' % key] = 5.

        Model['p_AffExc_%s' % key] = 0.04
        Model['p_AffInh_%s' % key] = 0.04

        Model[key+'_Gl'] = 10.
        Model[key+'_Cm'] = 200.
        Model[key+'_Trefrac'] = 3.
        Model[key+'_El'] = -60.
        Model[key+'_Vthre'] = -50.
        Model[key+'_Vreset'] = -60.
        Model[key+'_deltaV'] = 1.
        Model[key+'_a'] = 0.
        Model[key+'_b'] =  0.
        Model[key+'_tauw'] = 1e9

    # %%

    for model in ['classical', 'updated']:

        NTWK = ntwk.build.populations(Model, POPS,
                                        AFFERENT_POPULATIONS=['AffExc', 'AffInh'],
                                        with_raster=True,
                                        with_Vm=[4,1,1,1,1],
                                        verbose=True)

        #######################################
        ########### AFFERENT INPUTS ###########
        #######################################

        t_array = ntwk.arange(int(Model['tstop']/Model['dt']))*Model['dt']

        for key in POPS:
            Model['Fexc_%s' % key] = 350.+0.*t_array
            Model['Finh_%s' % key] = 700.+0.*t_array

        context_cond = (t_array>600) & (t_array<1300)

        Model['Fexc_PyrExc'][context_cond] += 20.
        Model['Fexc_PvInh'][context_cond] += 40.
        Model['Fexc_ChInh'][context_cond] += 40.
        Model['Fexc_VipInh'][context_cond] += 100.
        Model['Fexc_SstInh'][context_cond] -= 50.
        Model['Fexc_SstInh'][~context_cond] += 50.
        if model=='updated':
            Model['Fexc_ChInh'][context_cond] += 50.
            Model['Fexc_PyrExc'][context_cond] -= 10.

        stim_cond = (t_array>1000) & (t_array<1100)

        Model['Fexc_PyrExc'][stim_cond] += 110
        Model['Fexc_PvInh'][stim_cond] += 30
        Model['Fexc_SstInh'][stim_cond] += 50

        if model=='updated':
            # Model['Fexc_ChInh'][context_cond] += 100.
            Model['Finh_PyrExc'][stim_cond] += 50


        # # # afferent excitation onto cortical excitation and inhibition
        for i, tpop in enumerate(POPS):
            ntwk.stim.construct_feedforward_input(NTWK, tpop, 'AffExc',
                                                    t_array, Model['Fexc_%s' % tpop],
                                                    verbose=True,
                                                    SEED=10*(i+1))
            ntwk.stim.construct_feedforward_input(NTWK, tpop, 'AffInh',
                                                    t_array, Model['Finh_%s' % tpop],
                                                    verbose=True,
                                                    SEED=2*(i+1))

        ################################################################
        ## --------------- Initial Condition ------------------------ ##
        ################################################################
        ntwk.build.initialize_to_rest(NTWK)

        #####################
        ## ----- Run ----- ##
        #####################
        network_sim = ntwk.collect_and_run(NTWK, verbose=True)

        ntwk.recording.write_as_hdf5(NTWK, filename='%s.h5' % model)


    # %%
    # ######################
    # ## ----- Plot ----- ##
    # ######################

    COLORS = ['#008080', '#d40000', '#800080','#ff6600', '#800000']

    ## load file
    for model in ['classical', 'updated']:

        data = ntwk.recording.load_dict_from_hdf5(\
                                            '%s.h5' % model)

        fig, AX = ntwk.plots.pretty(data, 
                                COLORS=COLORS,
                        axes_extents = dict(Raster=1, Vm=2),
                        Raster_args=dict(ms=1.5, with_annot=False, subsampling=2),
                        Vm_args=dict(subsampling=1, lw=0.3, shift=40.,
                                    clip_spikes=False, vpeak=0),
                fig_args=dict(ax_scale=(1.4, .9), dpi=150,
                                hspace=0.1, bottom=0.2, top=0.2, 
                                left=0.1, right = 0.1))
        ylim = AX[-1].get_ylim()
        AX[-1].plot([600, 1300], (ylim[1]-4)*np.ones(2), '-', color='lightgrey', lw=2)
        AX[-1].plot([1000, 1100], (ylim[1]-3)*np.ones(2), 'k-', lw=1)
        AX[-1].set_ylim([ylim[1]-5, ylim[0]])
        fig.savefig(os.path.expanduser('~/Desktop/%s.svg' % model))
        
    
        
    # %%
    data

    # %%
