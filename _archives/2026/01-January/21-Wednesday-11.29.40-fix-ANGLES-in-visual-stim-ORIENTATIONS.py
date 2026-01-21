# %%

### IMPORT THE VALUES TO REPLACE FROM A GIVEN DATAFILE ###

import os, sys, pathlib
import numpy as np

if False:
    sys.path += ['./physion/src']
    from physion.analysis.read_NWB\
                            import scan_folder_for_NWBfiles, Data
    from physion.analysis.process_NWB import EpisodeData

    filename='/Users/yann/CURATED/Cibele/PV-cells_WT_Young_V1/NWBs/2025_10_10-16-52-46.nwb'
    data = Data(filename)
    ep = EpisodeData(data)

    old_angles = ep.varied_parameters['angle']
    new_angles = np.linspace(0, 157.5, len(old_angles))
    print(new_angles)

# %%
old_angles = [0.9, 23.27142857, 45.64285714,\
               68.01428571, 90.38571429,\
                112.75714286, 135.12857143, 157.5]
new_angles = np.linspace(0, 157.5, len(old_angles))

### LOOP OVER ALL FILES AND REPLACE THE VALUES ###
filenames = pathlib.Path(\
                os.path.expanduser('~/CURATED/Cibele')\
                    ).glob('**/visual-stim.npy')

for i, f in enumerate(filenames):

    if i<2000:
        print(i, ') ', f)

        try:
            stim = np.load(f, allow_pickle=True).item()
            stim['angle'] = np.array(stim['angle'])
            print(np.unique(stim['angle']))

            if 'angle' in stim:
                if len(np.unique(stim['angle']))==3:
                    # print('0', np.sum(np.array(stim['angle'])==0.))
                    # print('90', np.sum(np.array(stim['angle'])==90.))
                    # print('157.5', np.sum(np.array(stim['angle'])==157.5))
                    stim['angle'][stim['angle']==157.5]=0.
                elif len(np.unique(stim['angle']))==8:
                    for o, n in zip(np.unique(stim['angle']), new_angles):
                        stim['angle'][stim['angle']==o]=n

            print(np.unique(stim['angle']))
            np.save(f, stim)
        except BaseException as be:
            print(' [!!] Pb with ', f)
# %%
