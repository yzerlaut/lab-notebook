# %% [markdown]
# # Build Tuning Dataset across Conditions

# %%
import os, sys
import numpy as np

sys.path += ['./physion/src']
import physion
from physion.analysis.read_NWB\
                         import scan_folder_for_NWBfiles, Data
from physion.analysis.process_NWB import EpisodeData
from physion.analysis.protocols.orientation_tuning\
                        import compute_tuning_response_per_cells


# load dataset:
from Dataset_Organization import *

# %% [markdown]
# # Tuning Analysis Parameters

# %%

nMIN_DATAFILES = 2
nMIN_ROIs = 4

dFoF_parameters = dict(\
        roi_to_neuropil_fluo_inclusion_factor=1.15,
        neuropil_correction_factor = 0.7,
        method_for_F0 = 'sliding_percentile',
        percentile=5., # percent
        sliding_window = 5*60, # seconds
)

stat_test_props=dict(interval_pre=[-1.,0],
                     interval_post=[1.,2.],                                   
                     test='ttest',                                            
                     sign='positive')

response_significance_threshold=5e-2

# %% [markdown]
# # Compute Tuning Summary for All Conditions

# %%

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

    Tunings = []

    if len(DATASET['files'][cond])>nMIN_DATAFILES:

        for i, f in enumerate(DATASET['files'][cond]):

                print('%i) ' % (i+1), 'analyzing file: %s  [...] ' % f)
                data = Data(f, verbose=False)
                protocol_name=[p for p in data.protocols if '8orientation' in p][0]
                data.build_dFoF(**dFoF_parameters, verbose=False)

                if data.nROIs>=nMIN_ROIs:

                    try:
                        Episodes = EpisodeData(data, 
                                               quantities=['dFoF'], 
                                               protocol_name=protocol_name, 
                                               verbose=False)

                        Tuning = compute_tuning_response_per_cells(data, Episodes, 
                                                                    quantity='dFoF', 
                                                                    stat_test_props = stat_test_props, 
                                                                    response_significance_threshold =\
                                                                        response_significance_threshold, 
                                                                    contrast =\
                                                                        float(c.split('contrast-')[1][:3]))
                        Tuning['datafile'] = f

                        Tunings.append(Tuning)
                        print('      [v] --> included, n=%i ROIs ' % data.nROIs)
                    except BaseException as be:
                        print('                        [-------------------------------]')
                        print(be)
                        print()
                        print('      [X] --> discarded, problem in datafile, CHECK [!!]')
                        print('                        [-------------------------------]')

                else:
                    print('      [X] --> discarded, n=%i ROIs ' % data.nROIs)

        # # saving data
        np.save(os.path.join(summary_folder, 'Tunings_%s.npy' % c), Tunings)

    else:
        print()
        print('   [!!]   DATASET NOT LARGE ENOUGH   [!!] ')
        print('               only N=%i sessions available' %\
                                    len(DATASET['files'][cond]))
        print('   [!!]   DATASET not analyzed       [!!] ')
        print()


    print('-----------------------------------------------------------------')
    print('=================================================================')

# %%
