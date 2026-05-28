"""
reproducing protocol from:
  http://www.nature.com/doifinder/10.1038/nn.3920

blocks of 100s for gratings drifting at 1cycle/s but refreshed only @ 2Hz
                    --> phase reversing 
"""
import os
import itertools

Screen="Dell-2020"

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

def GratingPhaseReversing(Orientation, Screen, Nrepeat, 
                          Duration=100.0):
  return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "grating",
    "Screen": "%s",
    "movie_refresh_freq": 2.0,
    "-----------------------------------------------------------------1":0,
    "presentation-duration": %.1f,
    "presentation-interstim-period": 30.0,
    "presentation-prestim-period": 30.0,
    "presentation-poststim-period": 30.0,
    "presentation-blank-screen-color": 0.5,
    "N-repeat": %i,
    "-----------------------------------------------------------------3":0,
    "angle": %.1f,
    "speed": 1.0,
    "spatial-freq":0.05, 
    "screen-color": 1.0
  }
  """ % (Screen, Duration, Nrepeat, Orientation)

def MixedNovelFamiliar(NovelOrientation, FamiliarOrientation, 
                       Screen, Nrepeat, Duration):
   
  mixed = """{
    "Presentation": "multiprotocol",
    "shuffling" :"full",
    "shuffling-seed" :34,
    "movie_refresh_freq":2.0,
    "units":"cm",
    "presentation-prestim-period": 30.0,
    "presentation-poststim-period": 30.0,
    "presentation-interstim-period": 30.0,
    "presentation-blank-screen-color": 0.5,
    "Screen": "%s",
  """ % Screen

  i = 1 # protocol counter
  for Orientation in [FamiliarOrientation, NovelOrientation]:
      protocol = GratingPhaseReversing(Orientation, Screen, Nrepeat, Duration)
      if protocol!='':
          with open('protocol-%i.json' % i, 'w') as f:
              f.write(protocol)
      mixed += '  "Protocol-%i": "protocol-%i.json",\n' % (i, i)
      i += 1

  mixed = mixed[:-2]+'}'

  return mixed 


if 1:
  # build_movie(GratingPhaseReversing(45.0, Screen, 10), name='Learning-Familiar-Grating-45deg')#, rm=False)
  build_movie(MixedNovelFamiliar(135.0, 45.0, Screen, 20, 10.0), name='Testing-Novel-Familiar-Grating-135deg-45deg')#, rm=False)