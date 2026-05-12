import os
import itertools

# Screen="Dell-2020-low-resolution"
# Screen="LN-VR-3screens"
Screen="LN-2screens"

# stimulus-center position:
Saccade_Amplitude="200.0"

x=45.
y=10.

def build_movie(X, name='temp', rm=True):
  with open('%s.json' % name, 'w') as f:
    f.write(X)
  os.system('cd physion/src; python -m physion.visual_stim.build ../../%s.json; cd ../..' % name)
  if rm:
    os.remove('%s.json' % name)


###########################################
###      flashed stimuli                ###
###########################################

def FS(Screen, Nrepeat):
  return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "uniform_bg",
    "Screen": "%s",
    "-----------------------------------------------------------------1":0,
    "presentation-duration": 1.0,
    "presentation-interstim-period": 5.0,
    "presentation-blank-screen-color": 0.25,
    "N-repeat": %i,
    "-----------------------------------------------------------------3":0,
    "screen-color": 1.0
  }
  """ % (Screen, Nrepeat)


#################################################
###      quick-spatial mapping protocol       ###
#################################################

def QM(Screen, Nrepeat):
  return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "grating",
    "Screen": "%s",
    "-----------------------------------------------------------------1":0,
    "presentation-duration": 1,
    "presentation-interstim-period": 1.0,
    "N-repeat": %i,
    "-----------------------------------------------------------------2":0,
    "x-center-1": 15.0, "x-center-2": 75.0, "N-x-center": 3,
    "y-center-1": -20.0, "y-center-2": 20.0, "N-y-center": 3,
    "-----------------------------------------------------------------3":0,
    "spatial-freq": 0.06,
    "y-center":0.0,
    "speed":2,
    "angle": 0,
    "radius": 10
  }
  """ % (Screen, Nrepeat)

############################################
###      detailed mapping protocol       ###
############################################

Nrepeat=1
def DM(Screen, Nrepeat):
   return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "grating",
    "Screen": "%s",
    "shuffling" :"full",
    "shuffling-seed" :34,
    "-----------------------------------------------------------------1":0,
    "presentation-duration": 1,
    "presentation-interstim-period": 1.0,
    "N-repeat": %i,
    "-----------------------------------------------------------------2":0,
    "x-center-1": 0.0, "x-center-2": 90.0, "N-x-center": 7,
    "y-center-1": -20.0, "y-center-2": 40.0, "N-y-center": 4,
    "angle-1": 0.0, "angle-2": 135.0, "N-y-center": 4,
    "-----------------------------------------------------------------3":0,
    "spatial-freq": 0.06,
    "conrtast":0.8,
    "speed":0,
    "angle": 0,
    "radius": 10
  }
  """ % (Screen, Nrepeat)

###########################################
###      foud-Dim of visual infos       ###
###########################################

def FD(Screen, Nrepeat):
   
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

  return fourDimVisualInfo


if 1:
  build_movie(FS(Screen, 50), name='flashed-stimuli')#, rm=False)
  build_movie(FD(Screen, 20), name='4-DIM-visual-information')#, rm=False)
  build_movie(QM(Screen, 10), name='quick-mapping')#, rm=False)
  build_movie(DM(Screen, 10), name='detailed-mapping')#, rm=False)

if 0:
  build_movie(DM(Screen, 1), name='detailed-mapping')#, rm=False)

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