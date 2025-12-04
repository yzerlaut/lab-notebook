# %%
import sys, os
sys.path += ['physion/src']
import physion

folder = os.path.expanduser('~/DATA/physion_Demo-Datasets')

dataset, subjects, _ = physion.assembling.dataset.read_spreadsheet(\
                                    os.path.join(folder, 'PV-WT', 'DataTable.xlsx'))

DS = physion.analysis.read_NWB.scan_folder_for_NWBfiles(\
                                        os.path.join(folder, 'PV-WT', 'NWBs'))

# %%

# %%