import sys, os, shutil
sys.path += ['physion/src']
import physion

for dataset in [\
        'SST-cells_WT_Adult_V1_Taddy',
        'SST-cells_cond-GluN1-KO_Adult_V1_Taddy']:

    data, _, _ =\
            physion.assembling.dataset.read_spreadsheet(\
                os.path.expanduser('~/CURATED/Cibele/%s/DataTable.xlsx' % dataset),
                get_metadata_from='table')
    for day, time in zip(data['day'], data['time']):
        if os.path.isdir(\
                os.path.expanduser('~/UNPROCESSED/SST-WT-GluN1KO-GluN3KO-2023/processed/%s/%s' % (day, time))):
            shutil.copytree(\
                os.path.expanduser('~/UNPROCESSED/SST-WT-GluN1KO-GluN3KO-2023/processed/%s/%s' % (day, time)),
                os.path.expanduser('~/CURATED/Cibele/%s/processed/%s/%s' % (dataset, day, time)))
            print('[v]', dataset, day, time)
        else:
            print('[X]', dataset, day, time) 
        