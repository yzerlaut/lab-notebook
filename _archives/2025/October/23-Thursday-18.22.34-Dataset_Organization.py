import os

summary_folder = os.path.join(os.path.expanduser('~'), 
                              'CURATED', 'Cibele', 'summary')

conditions = [
    # 'hsyn-PV-cells_WT_Young_V1'
    'PV-cells_WT_Adult_V1',
    'PV-cells_cond-GluN1-KO_Adult_V1',
    'SST-cells_WT_Adult_V1',
    'PV-cells_WT_Young_V1',
    # 'PV-cells_cond-GluN1-KO_Young_V1',
    #'SST-cells_WT_Young_V1',
]
base_path = os.path.expanduser('~/CURATED/Cibele/')

AGE_INTERVALS = [\
    (15,19), (20,23), (24,27)]

datasets = {}
for c in conditions:

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

# SOME MANUAL CHANGES UNTIL DATA ARE CURATED !
for c in datasets:
    # if ('PV-cells_WT_Young' in c) or ('PV-cells_WT_P' in c):
        # datasets[c]['datafolder'] = '/media/user/Data/Cibele/PV_BB_V1/NWBs'
    # if ('SST-cells_WT_Young' in c) or ('SST-cells_WT_P' in c):
        # datasets[c]['datafolder'] = '/home/user/DATA/Cibele/SST_BB_V1/NWBs'
    if ('hsyn-PV' in c): 
        datasets[c]['datafolder'] = '/home/user/DATA/Cibele/PYR-PV_BB_V1/NWBs'


if __name__=='__main__':
    from pprint import pprint
    pprint(datasets)

