import os
import itertools

# Screen="Dell-2020-low-resolution"
Screen="LN-VR-3screens"

# stimulus-center position:
x=-45.
y=0. 

# 
Saccade_Amplitude = '50.0' # 200.0

def build_movie(X, name='temp', rm=True):

  with open('%s.json' % name, 'w') as f:
    f.write(X)
  os.system('cd physion/src; python -m physion.visual_stim.build ../../%s.json; cd ../..' % name)
  if rm:
    os.remove('%s.json' % name)


###########################################
###      spatial mapping protocol       ###
###########################################

Nrepeat=10
SM = """{
  "Presentation": "Stimuli-Sequence",
  "Stimulus": "grating",
  "Screen": "%s",
  "-----------------------------------------------------------------1":0,
  "presentation-duration": 1,
  "N-repeat": %i,
  "-----------------------------------------------------------------2":0,
  "x-center-1": -75.0, "x-center-2": -15.0, "N-x-center": 3,
  "y-center-1": -20.0, "y-center-2": 20.0, "N-y-center": 3,
  "-----------------------------------------------------------------3":0,
  "spatial-freq": 0.06,
  "y-center":0.0,
  "speed":2,
  "angle": 0,
  "radius": 10
}
""" % (Screen, Nrepeat)

###########################################
###      spatial mapping protocol       ###
###########################################

Nrepeat = 10
fourDimVisualInfo = """{
  "Presentation": "multiprotocol",
  "shuffling" :"full",
  "shuffling-seed" :34,
  "movie_refresh_freq":30.0,
  "units":"cm",
  "presentation-prestim-period": 15.0,
  "presentation-poststim-period": 5.0,
  "presentation-interstim-period": 3.0,
  "presentation-blank-screen-color": 0.5,
  "Screen": "%s",
""" % Screen

def single_protocol(spatial, temporal, contrast, size):
    if (spatial=='high') and (temporal=='high'):
        protocol = """{
  "Presentation": "Stimulus-Sequence",
  "Stimulus": "natural-image+VSE",
  "presentation-duration": 4.0,
  "presentation-interstim-period": 3.0,
  "N-repeat": %i,
  "_______________________________________________________________________1":0,
  "min-saccade-duration": 0.2,
  "max-saccade-duration": 1.0,
  "saccade-amplitude": %s,
  "seed": 0,
  "contrast": %.2f,
  "radius": %.2f,
  "x-center": %.2f,
  "y-center": %.2f,
  "_______________________________________________________________________2":0,
  "Image-ID-1": 0, "Image-ID-2": 3, "N-Image-ID": 2,
  "Screen": "%s"
}""" % (Nrepeat, Saccade_Amplitude, contrast, size, x, y, Screen)
    elif (spatial=='high') and (temporal=='low'):
        protocol = """{
  "Presentation": "Stimulus-Sequence",
  "Stimulus": "natural-image",
  "presentation-duration": 2.0,
  "presentation-interstim-period": 3.0,
  "N-repeat": %i,
  "_______________________________________________________________________1":0,
  "contrast": %.2f,
  "radius": %.2f,
  "x-center": %.2f,
  "y-center": %.2f,
  "_______________________________________________________________________2":0,
  "Image-ID-1": 0, "Image-ID-2": 3, "N-Image-ID": 2,
  "Screen": "%s"
}""" % (Nrepeat, contrast, size, x, y, Screen)
    elif (spatial=='low') and (temporal=='low'):
        protocol = """{
  "Presentation": "Stimulus-Sequence",
  "Stimulus": "grating",
  "presentation-duration": 2.0,
  "presentation-interstim-period": 3.0,
  "N-repeat": %i,
  "_______________________________________________________________________1":0,
  "contrast": %.2f,
  "radius": %.2f,
  "x-center": %.2f,
  "y-center": %.2f,
  "spatial-freq":0.04,
  "_______________________________________________________________________2":0,
  "angle-1": 0, "angle-2": 90, "N-angle": 2,
  "Screen": "%s"
}""" % (Nrepeat, contrast, size, x, y, Screen)
    elif (spatial=='low') and (temporal=='high'):
        protocol = """{
  "Presentation": "Stimulus-Sequence",
  "Stimulus": "grating-VSE",
  "presentation-duration": 4.0,
  "presentation-interstim-period": 3.0,
  "N-repeat": %i,
  "_______________________________________________________________________1":0,
  "min-saccade-duration": 0.2,
  "max-saccade-duration": 1.0,
  "saccade-amplitude": %s, 
  "seed": 0,
  "contrast": %.2f,
  "radius": %.2f,
  "x-center": %.2f,
  "y-center": %.2f,
  "spatial-freq":0.04,
  "_______________________________________________________________________2":0,
  "angle-1": 0, "angle-2": 90, "N-angle": 2,
  "Screen": "%s"
}""" % (Nrepeat, Saccade_Amplitude, contrast, size, x, y, Screen)
    else:
        print('protocol not recognized !!')
        protocol = ''

    return protocol 


if True:

  i = 1 # protocol counter

  for spatial, temporal, contrast, size in itertools.product(\
    ['low', 'high'], ['low', 'high'], [0.2, 1.0], [15., 50.]):
      protocol = single_protocol(spatial, temporal, contrast, size) 
      if protocol!='':
          with open('protocol-%i.json' % i, 'w') as f:
              f.write(protocol)
      fourDimVisualInfo += '  "Protocol-%i": "protocol-%i.json",\n' % (i, i)
      i += 1

  fourDimVisualInfo = fourDimVisualInfo[:-2]+'}'
  build_movie(fourDimVisualInfo, name='4-DIM-visual-information')


if True:
  build_movie(SM, name='spatial-mapping', rm=False)

if False:
  # build_movie(SM, name='spatial-mapping', rm=False)
  import json
  with open('spatial-mapping.json', 'r') as f:
     stim = json.load(f)
  import sys
  sys.path.append('./physion/src')
  from physion.visual_stim.build import build_stim
  Stim = build_stim(stim)

  import matplotlib.pylab as plt
  import numpy as np

  im = Stim.get_image(1).T
  print(im.min(), im.mean(), im.max())
  im = np.uint8(255.*im)
  print(im.min(), im.mean(), im.max())
  plt.imshow(im, vmin=0, vmax=255)
  plt.show()