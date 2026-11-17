# %%
import os, sys
from multiprocessing import Pool

sys.path += ['physion/src']

from physion.analysis.read_NWB import Data,\
                    scan_folder_for_NWBfiles 
from physion.analysis.episodes.build import EpisodeData


# %%

def save_all_epData(filename,
        quantities = ['running', 'spikes', 'firing', 'MUA']):

    data = Data(filename)
    data.build(quantities)

    for i, p in enumerate(data.protocols):

        ep = EpisodeData(data,
                        protocol_name=p,
                        quantities=quantities)
        ep.save('temp/')

        # for index in np.unique(ep.index):
        #     #
        #     protocol = \
        #         get_stimKey_from(data, i,
        #                         ep.contrast[0], 
        #                         ep.radius[0], 
        #                         index)
        #     index_cond = (ep.index==index)

        #     temp_file = 'temp/%s-%s.npy' % (\
        #         os.path.basename(filename).replace('.nwb',''),
        #             protocol)

        #     if not os.path.isfile(temp_file):

        #         d = {}
        #         d['duration'] = ep.time_duration[0]
        #         d['t'] = ep.MUA[index_cond,:,:]
        #         d['MUA'] = ep.MUA[index_cond,:,:]
        #         d['spikes'] = ep.spikes[index_cond,:,:]
        #         stim_cond = (ep.t>0) & (ep.t<2)
        #         d['running'] = ep.running[:,stim_cond].mean(axis=1)[index_cond]
        #         np.save(temp_file, d)
        #         print('saved: ', temp_file)

# %%
# def temp_print(filename):
#     print(filename)

if __name__ == '__main__':

    datafolder = os.path.join(os.path.expanduser('~'), 
                        'DATA', 'Sally', 'Npx-WT-2026')

    dataset = scan_folder_for_NWBfiles(datafolder,
                                    for_protocol='4dim')
    # filenames = [\
    #     '2026_07_28-19-09-20',
    #     '2026_07_29-17-47-23',
    #     '2026_07_30-17-32-01',
    #     '2026_07_31-17-50-18',
    #     '2026_08_18-18-14-18',
    #     '2026_08_19-18-54-17',
    #     '2026_08_20-17-38-39',
    #     '2026_08_21-18-04-34',
    #     '2026_08_25-18-13-15',
    #     '2026_08_26-17-46-18',
    #     ]
    # dataset = scan_folder_for_NWBfiles(datafolder, for_protocol='4dim', from_filenames=filenames)

    with Pool() as p:
        print(p.map(save_all_epData, dataset['files']))
        # print(p.map(temp_print, dataset['files']))
# %%
