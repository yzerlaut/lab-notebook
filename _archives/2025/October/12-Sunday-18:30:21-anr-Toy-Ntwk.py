# %%
import sys, pathlib
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
