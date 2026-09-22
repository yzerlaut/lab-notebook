# %%
import os, sys, pathlib
import numpy as np
from multiprocessing import Pool

sys.path += ['physion/src']

from physion.analysis.read_NWB import Data,\
                    scan_folder_for_NWBfiles 
from physion.analysis.episodes.build import EpisodeData

# create temp directory if it doesn't exist
pathlib.Path('./temp').mkdir(parents=True, exist_ok=True)

# %%
datafolder = os.path.join(os.path.expanduser('~'), 
                    'DATA', 'Sally', 'Npx_WT_prelim_2026')

dataset = scan_folder_for_NWBfiles(datafolder,
                                   for_protocol='4dim')

# %%

def get_stimKey_from(data, protocol_id, contrast, radius, index):

    abbrev = ''
    stim_type = data.metadata['Protocol-%i-Stimulus' % (protocol_id+1)]
    if 'natural' in stim_type: 
        abbrev += 's+'
    else: 
        abbrev += 's-'
    if 'VSE' in stim_type: 
        abbrev += 't+'
    else: 
        abbrev += 't-'
    if contrast>0.5: 
        abbrev += 'c+'
    else: 
        abbrev += 'c-'
    if radius>=20.: 
        abbrev += 'e+'
    else: 
        abbrev += 'e-'
    if index==1: 
        abbrev += '2' 
    else: 
        abbrev += '1'
    return abbrev

def save_all_epData(filename,
        quantities = ['running', 'spikes', 'MUA']):

    data = Data(filename)
    data.build(quantities)

    for i, p in enumerate(data.protocols):

        ep = EpisodeData(data,
                        protocol_name=p,
                        quantities=quantities)

        for index in np.unique(ep.index):
            #
            protocol = \
                get_stimKey_from(data, i,
                                ep.contrast[0], 
                                ep.radius[0], 
                                index)
            index_cond = (ep.index==index)

            temp_file = 'temp/%s-%s.npy' % (\
                os.path.basename(filename).replace('.nwb',''),
                    protocol)

            if not os.path.isfile(temp_file):

                d = {}
                d['duration'] = ep.time_duration[0]
                d['t'] = ep.MUA[index_cond,:,:]
                d['MUA'] = ep.MUA[index_cond,:,:]
                d['spikes'] = ep.spikes[index_cond,:,:]
                stim_cond = (ep.t>0) & (ep.t<2)
                d['running'] = ep.running[:,stim_cond].mean(axis=1)[index_cond]
                np.save(temp_file, d)
                print('saved: ', temp_file)

# %%
def temp_print(filename):
    print(filename)

if __name__ == '__main__':
    with Pool() as p:
        print(p.map(save_all_epData, dataset['files']))
        # print(p.map(temp_print, dataset['files']))
# %%
