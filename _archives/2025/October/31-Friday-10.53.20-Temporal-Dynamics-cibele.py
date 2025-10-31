# %% [markdown]
# # Build Deconvolved Responses across Conditions

# %%
import os, sys , shutil 
import multiprocessing
import numpy as np

sys.path += ['./physion/src']
from physion.analysis.read_NWB\
                         import scan_folder_for_NWBfiles, Data
from physion.analysis.process_NWB import EpisodeData
from physion.analysis.protocols.orientation_tuning\
                        import compute_tuning_response_per_cells

# %% 
########################################################
###      build DATASETS of different conditions  #######
########################################################

base_path = os.path.expanduser('~/CURATED/Cibele/')
folders = [
    "PV-cells_WT_Adult_V1", 
    "PV-cells_WT_Young_V1", 
    "PV-cells_cond-GluN1-KO_Adult_V1", 
    "PYR-PV-SynGCaMP_WT_Young_V1",
    "SST-cells_cond-GluN1-KO_Young_V1",
    "SST-cells_WT_Adult_V1",
    "SST-cells_WT_Young_V1",
    "SST-cells_cond-GluN1-KO_Adult_V1_Taddy",
    "SST-cells_WT_Adult_V1_Taddy"
]

# age intervals in Yound
AGE_INTERVALS = [\
    (15,19), (20,23), (24,27), (16,21), (22,27)]

# to be a valid dataset:
nMIN_DATAFILES = 2

summary_folder = os.path.join(os.path.expanduser('~'), 
                              'CURATED', 'Cibele', 'summary')

datasets = {}
for c in folders:

    for contrast in [0.5, 1.0]:

        datasets[c+'_contrast-%.1f' % contrast] =\
              {'datafolder':os.path.join(base_path, c, 'NWBs'), 
                'age_interval':None}
        
        # we split young animals into age groups
        if 'Young' in c:
            for interval in AGE_INTERVALS:
                datasets[c.replace('Young', 'P%i-P%i' % interval)+'_contrast-%.1f' % contrast] =\
                    {'datafolder':os.path.join(base_path, c, 'NWBs'), 
                        'age_interval':interval}
                
# %%
def process_file(filename, i, c):

    # to be a valid datafile:
    nMIN_ROIs = 4
    # calcium pre-processing params
    dFoF_parameters = dict(\
            roi_to_neuropil_fluo_inclusion_factor=1.15,
            neuropil_correction_factor = 0.7,
            method_for_F0 = 'sliding_percentile',
            percentile=5., # percent
            sliding_window = 5*60, # seconds
    )
    TAU_DECONVOLUTION = 0.8

    # statistical test for visually-evoked-responses
    stat_test_props=dict(interval_pre=[-1.,0],
                         interval_post=[1.,2.],                                   
                         test='ttest',                                            
                         sign='positive')

    response_significance_threshold=5e-2

    print('%i) ' % (i+1), 'analyzing file: %s  [...] ' % filename)
    data = Data(filename, verbose=False)
    protocol_name=[p for p in data.protocols if '8orientation' in p][0]
    data.build_dFoF(**dFoF_parameters, verbose=False)

    quantities = ['Deconvolved']
    if 'Running-Speed' in data.nwbfile.acquisition:
        quantities += ['running_speed']

    if data.nROIs>=nMIN_ROIs:

        try:
            # deconvolve first:
            data.build_Deconvolved(Tau=TAU_DECONVOLUTION)
            # process episodes
            Episodes = EpisodeData(data, 
                                    quantities=quantities,
                                    protocol_name=protocol_name, 
                                    verbose=False)

            epCond = Episodes.find_episode_cond(key='contrast',
                                                value=float(c.split('contrast-')[1][:3]))

            significant = np.zeros(data.nROIs, dtype=bool)
            for i in range(data.nROIs):
                    cell_resp = Episodes.compute_summary_data(stat_test_props,
                                                              exclude_keys=['repeat', 'angle'],
                                                              response_args=dict(quantity='Deconvolved',
                                                                                 roiIndex=i))
                    cond = (cell_resp['contrast']==contrast)
                    significant[i] = cell_resp['significant'][cond][0]
                    
            Response = {
                    't':Episodes.t,
                    'Deconvolved':Episodes.Deconvolved[epCond,:,:].mean(axis=0),
                    'significant':significant,
                    'nROIs_original': data.original_nROIs,
                    'nROIs_final': data.nROIs,

            }

            np.save(os.path.join(summary_folder, 'temp', 
                                 'tempResponse-%s-%i.npy' % (c, i)),
                    Response)
            print('      [v] --> included, n=%i ROIs ' % data.nROIs)
        except BaseException as be:
            print('                        [-------------------------------]')
            print(be)
            print()
            print(filename)
            print('nROIs=%i' % data.nROIs, ', protocols=%s' % data.protocols)
            print(Episodes.varied_parameters)
            print('      [X] --> discarded, problem in datafile, CHECK [!!]')
            print('                        [-------------------------------]')

    else:
        print('      [X] --> discarded, n=%i ROIs ' % data.nROIs)


if __name__=='__main__':

    import physion

    cpus = multiprocessing.cpu_count()-1 # leaving 1 cpu for the rest

    # temporary folder for parallelization
    os.makedirs(os.path.join(summary_folder, 'temp'), exist_ok=True)

    Nstart = 0
    Nend = len(datasets)

    for n in range(Nstart, Nend):

        c = list(datasets.keys())[n]

        table = datasets[c]['datafolder'].replace('NWBs', 'DataTable.xlsx')

        dataset_table, subjects_table, analysis =\
                physion.assembling.dataset.read_spreadsheet(table,
                    get_metadata_from='table')
        print()
        print()
        print('=================================================================')
        print('-----------------------------------------------------------------')
        print('------- %i) computing : %s ' % (n, c))
        print('-----------------------------------------------------------------')
        print()

        DATASET = scan_folder_for_NWBfiles(datasets[c]['datafolder'])
        
        # FILTER
        # 1) protocol type: orientation tuning
        cond = np.array([np.sum(['8orientation' in p for p in protocols])\
                        for protocols in DATASET['protocols']], dtype=bool)
        # 2) age condition
        if datasets[c]['age_interval'] is not None:
            cond = cond &\
                (DATASET['ages']>=datasets[c]['age_interval'][0]) &\
                (DATASET['ages']<=datasets[c]['age_interval'][1])


        if len(DATASET['files'][cond])>nMIN_DATAFILES:

            ################################################
            ###    parallelization here !   #################
            ################################################
            nruns = int(len(DATASET['files'][cond])/cpus)+1

            for r in range(nruns):
                i0 = r*cpus
                imax = np.min([i0+cpus, len(DATASET['files'][cond])]) 
                print(' - running set of files %i:%i' % (i0, imax))

                # start the processes
                procs = []
                for i in range(i0,imax):
                    proc = multiprocessing.Process(\
                                        target=process_file, 
                                        args=(DATASET['files'][cond][i], i, c))
                    procs.append(proc)
                    proc.start()

                # complete the processes
                for proc in procs:
                    proc.join()

            #####################################
            ###### UN-PARALLELIZED VERSION ######
            # for i, f in enumerate(DATASET['files'][cond]):
            #     process_file(f, i, c)
            #####################################

            # now that we have stored all datafile outputs
            Responses = []
            for i, f in enumerate(DATASET['files'][cond]):

                if os.path.isfile(os.path.join(summary_folder, 'temp', 
                                              'tempResponse-%s-%i.npy' % (c, i))):
                    Response = np.load(os.path.join(summary_folder, 'temp', 
                                                'tempResponse-%s-%i.npy' % (c, i)),
                                        allow_pickle=True).item()
                    Responses.append(Response)

            # # saving data
            np.save(os.path.join(summary_folder, 'Deconvolved_%s.npy' % c), 
                    Responses)

        else:
            print()
            print('   [!!]   DATASET NOT LARGE ENOUGH   [!!] ')
            print('               only N=%i sessions available' %\
                                        len(DATASET['files'][cond]))
            print('   [!!]   DATASET not analyzed       [!!] ')
            print()

        print('-----------------------------------------------------------------')
        print('=================================================================')
    shutil.rmtree(os.path.join(summary_folder, 'temp'))

# %%
if False:

    import physion.utils.plot_tools as pt
    from scipy import stats

    def plot_response_dynamics(keys,
                               path=os.path.expanduser('~'),
                               average_by='sessions',
                               norm='',
                               colors=None,
                               with_label=True,
                               fig_args={}):
        
        if colors is None:
            colors = pt.plt.rcParams['axes.prop_cycle'].by_key()['color']

        if type(keys)==str:
            keys, colors = [keys], [colors[0]]

        fig, ax = pt.figure(**fig_args)
        x = np.linspace(-30, 180-30, 100)

        for i, (key, color) in enumerate(zip(keys, colors)):

                # load data
                Responses = \
                        np.load(os.path.join(path, 'Deconvolved_%s.npy' % key), 
                                allow_pickle=True)

                if average_by=='sessions':
                    # mean significant responses per session
                    Deconvolved = [np.mean(Response['Deconvolved'][Response['significant'],:],
                                    axis=0) for Response in Responses]

                elif average_by=='ROIs':
                    # mean significant responses per session
                    Deconvolved = np.concatenate([\
                                    Response['Deconvolved'][Response['significant'],:]\
                                                                for Response in Responses])

                if norm == 'min-max':
                    response = np.mean(Deconvolved, axis=0)
                    sresponse = stats.sem(Deconvolved, axis=0)
                    response -= response[Responses[0]['t']<0].mean()
                    sresponse /= response.max() # first sem
                    response /= response.max()
                    pt.plot(Responses[0]['t'], 
                            response, sy=sresponse,
                            color=color, ax=ax, ms=2)
                
                else:
                    pt.plot(Responses[0]['t'], 
                            np.mean(Deconvolved, axis=0), 
                                    sy=stats.sem(Deconvolved, axis=0), 
                                    color=color, ax=ax, ms=2)

                if with_label:

                    annot = i*'\n'
                    if average_by=='sessions':
                        annot += 'N=%02d %s, ' % (len(Deconvolved), average_by) + key
                    else:
                        annot += 'n=%04d %s, ' % (len(Deconvolved), average_by) + key

                    pt.annotate(ax, annot, (1., 0.9), va='top', color=color)

        pt.set_plot(ax, ylabel='(%s)\n$\Delta$F/F' % norm,  xlabel='time (s)')

        return fig, ax
    
    fig, ax = plot_response_dynamics(\
                        ['PV-cells_WT_Adult_V1_contrast-1.0', 
                         'PV-cells_WT_Adult_V1_contrast-0.5'],
                         colors=['tab:red', 'lightpink'],
                        # average_by='ROIs',
                        norm='min-max',
                        path=summary_folder)
    
    # %%