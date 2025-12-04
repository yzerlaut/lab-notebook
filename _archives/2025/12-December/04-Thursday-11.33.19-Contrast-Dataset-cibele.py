# %% [markdown]
# # Build Sensitivity Dataset across Conditions

# %%
import os, sys , shutil 
import multiprocessing
import numpy as np

sys.path += ['./physion/src']
from physion.analysis.read_NWB\
                         import scan_folder_for_NWBfiles, Data
from physion.analysis.process_NWB import EpisodeData
from physion.analysis.protocols.contrast_sensitivity\
                        import compute_sensitivity_per_cells

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

    for angle in [0., 90.]:

        datasets[c+'_angle-%.1f' % angle] =\
              {'datafolder':os.path.join(base_path, c, 'NWBs'), 
                'age_interval':None}
        
        # we split young animals into age groups
        if 'Young' in c:
            for interval in AGE_INTERVALS:
                datasets[c.replace('Young', 'P%i-P%i' % interval)+'_angle-%.1f' % angle] =\
                    {'datafolder':os.path.join(base_path, c, 'NWBs'), 
                        'age_interval':interval}
                
# %%
# to be a valid dataset:
nMIN_DATAFILES = 2

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
    # statistical test for visually-evoked-responses
    stat_test_props=dict(interval_pre=[-1.5,0],
                         interval_post=[0.,1.5],                                   
                         test='ttest',                                            
                         sign='positive')

    response_significance_threshold=5e-2

    print('%i) ' % (i+1), 'analyzing file: %s  [...] ' % filename)
    data = Data(filename, verbose=False)
    protocol_name=[p for p in data.protocols if '8contrast' in p][0]
    data.build_dFoF(**dFoF_parameters, verbose=False)

    if data.nROIs>=nMIN_ROIs:

        try:
            Episodes = EpisodeData(data, 
                                    quantities=['dFoF'], 
                                    protocol_name=protocol_name, 
                                    verbose=False)

            Sensitivity = compute_sensitivity_per_cells(data, Episodes, 
                                                        quantity='dFoF', 
                                                        stat_test_props=stat_test_props, 
                                                        response_significance_threshold = response_significance_threshold, 
                                                        angle = float(c.split('angle-')[1][:3]))

            Sensitivity['datafile'] = filename
            Sensitivity['nROIs_original'] = data.original_nROIs
            Sensitivity['nROIs_final'] = data.nROIs
            Sensitivity['subject'] = data.nwbfile.subject.subject_id

            np.save(os.path.join(summary_folder, 'temp', 
                                 'Sensitivity-%s-%i.npy' % (c, i)),
                    Sensitivity)
            print('      [v] --> included, n=%i ROIs ' % data.nROIs)
        except BaseException as be:
            print('                        [-------------------------------]')
            print(be)
            print()
            print('      [X] --> discarded, problem in datafile, CHECK [!!]')
            print('                        [-------------------------------]')

    else:
        print('      [X] --> discarded, n=%i ROIs ' % data.nROIs)

if __name__=='__main__':

    import physion

    if sys.platform=='linux':
        multiprocessing.set_start_method('spawn', force=True)

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
        # 1) protocol type: contrast sensitivity
        cond = np.array([np.sum(['8contrast' in p for p in protocols])\
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
            Sensitivitys = []
            for i, f in enumerate(DATASET['files'][cond]):

                if os.path.isfile(os.path.join(summary_folder, 'temp', 
                                              'Sensitivity-%s-%i.npy' % (c, i))):
                    Sensitivity = np.load(os.path.join(summary_folder, 'temp', 
                                                'Sensitivity-%s-%i.npy' % (c, i)),
                                        allow_pickle=True).item()
                    Sensitivitys.append(Sensitivity)

            # # saving data
            np.save(os.path.join(summary_folder, 'Sensitivities_%s.npy' % c), 
                    Sensitivitys)

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

    import sys, os
    sys.path += ['physion/src']
    import physion.utils.plot_tools as pt
    from physion.analysis.protocols.contrast_sensitivity\
            import plot_contrast_sensitivity, plot_contrast_responsiveness

    summary_folder =\
          os.path.expanduser('~/CURATED/Cibele/summary')
    folders = [
        "PV-cells_WT_Adult_V1", 
        "PV-cells_WT_Young_V1",
        "PV-cells_cond-GluN1-KO_Adult_V1", 
        "PYR-PV-SynGCaMP_WT_Young_V1",
        "SST-cells_cond-GluN1-KO_Young_V1",
        "SST-cells_WT_Adult_V1",
        "SST-cells_WT_Young_V1",
    ]
    for i, folder in enumerate(folders):
        fig, ax = plot_contrast_sensitivity(\
                                ['%s_angle-0.0' % folder, 
                                 '%s_angle-90.0' % folder],
                                # average_by='ROIs',
                                # average_by='subjects',
                                colors = [pt.tab10(i), 'lightgrey'],
                                path=summary_folder)


# %%
