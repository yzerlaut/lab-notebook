import itertools

# %%
# generate all stimulus keys:
all_stimKeys = []
for s,i,c,t,e in itertools.product(\
    ['+','-'], [1,2], ['+','-'], ['+','-'], ['+','-']):
    all_stimKeys.append('s%st%sc%se%s%i' %(s,t,c,e,i))

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

def stim_annot(ax, stim,
            xycoords='axes fraction', ha='right',
            loc=(0.29,1.05)):
    title = stim[1::2]+' '+'\n'+stim[::2]
    ax.annotate(title, loc, ha=ha, fontsize=7,
                xycoords=xycoords,
                linespacing=0.6, family='monospace')

if __name__=='__main__':
    print(all_stimKeys)