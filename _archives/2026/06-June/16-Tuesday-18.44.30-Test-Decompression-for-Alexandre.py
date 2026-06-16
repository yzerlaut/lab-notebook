# %%
import numpy as np
import os
from PIL import Image

root_folder = os.path.expanduser(\
    '~/DATA/physion_Demo-Datasets/PYR-WT/processed/2025_11_14/13-54-32/TSeries-11142025-001')

settings = {
    'original_folder': root_folder,
    'compressed_folder': root_folder,
    'ops_file': os.path.join(root_folder, 'suite2p/plane0/ops.npy'),
    'stat_file': os.path.join(root_folder, 'suite2p/plane0/stat.npy'),
    'iscell_file': os.path.join(root_folder, 'suite2p/plane0/iscell.npy'),
}

def list_tiffs(folder):

    return np.sort([f for f in os.listdir(folder)\
                     if '.ome.tif' in f])

def extract_fluo(settings):

    ops = np.load(settings['ops_file'],
                      allow_pickle=True).item()
    xoffset, yoffset = ops['xoff'], ops['yoff']

    stat = np.load(settings['stat_file'],
                    allow_pickle=True)
    iscell = np.load(settings['iscell_file'],
                allow_pickle=True)[:,0]==1

    fluo = {}
    for key in ['original', 'compressed']:
        # find list of tiffs
        tiffs = list_tiffs(settings['%s_folder' % key])
        # initialize data to zero
        fluo[key] = np.zeros((np.sum(iscell), 
                             len(tiffs)), dtype=np.int16)
        
        # loop over cells
        for c, cell in enumerate(np.arange(len(stat))[iscell]):

            # cellular mask:
            xmask = stat[cell]['xpix']
            ymask = stat[cell]['ypix']

            # loop over frames
            for frame, tiff in enumerate(tiffs):

                # load file
                fn = os.path.join(settings['%s_folder' % key], tiff)
                image = np.array(Image.open(fn), dtype=np.uint16)

                # extract 

                fluo[key][c,frame] =image[xmask+xoffset[frame],\
                                         ymask+yoffset[frame]].mean()
    return fluo

fluo = extract_fluo(settings)

# %%
def plot_before_after(settings, fluo):

    fig, AX = plt.subplots(10, 1, figsize=(6,4))
    plt.subplots_adjust(left=0.4, top=0.99)
    im = fig.add_axes([0,0.55,0.3,0.4])

    ops = np.load(settings['ops_file'],
                      allow_pickle=True).item()
    xoffset, yoffset = ops['xoff'], ops['yoff']

    stat = np.load(settings['stat_file'],
                    allow_pickle=True)
    iscell = np.load(settings['iscell_file'],
                allow_pickle=True)[:,0]==1

    img = ops['meanImg']**.1
    im.imshow(img, cmap=plt.cm.grey)
    for cell in np.arange(len(stat))[iscell]:
        xmask = stat[cell]['xpix']
        ymask = stat[cell]['ypix']
        im.scatter(xmask, ymask, color='y', 
                   s=0.2, alpha=.05)
    im.axis('off')
    im.set_title('n=%i cells' % np.sum(iscell))
    zoom = range(1000, 3000) 
    for ax, cell in zip(AX, np.random.choice(np.sum(iscell), 10)):
        ax.plot(fluo['original'][cell,zoom][::2], color='tab:green',lw=0.5)
        ax.plot(fluo['compressed'][cell,zoom][::2], color='tab:red', lw=0.2)
        if ax==AX[-1]:
            ax.set_xlabel('frame #')
        else:
            ax.set_xticklabels([])
        ax.set_ylabel('cell%i' % cell, fontsize=7)
    AX[0].annotate('original', (0,1.1), xycoords='axes fraction', color='tab:green')
    AX[0].annotate('(de)compressed', (1,1.1), xycoords='axes fraction', color='tab:red', ha='right')


    error = 100*np.mean(np.abs(fluo['original']-fluo['compressed'])/fluo['original'], axis=1)
    err = fig.add_axes([0.1,0.1,0.15,0.3])
    err.hist(error, color='k')
    err.set_ylabel('count (cell)')
    err.set_title('RMSE (%)')
    return fig

fig = plot_before_after(settings, fluo)

plt.show()