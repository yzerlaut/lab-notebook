"""
reproducing protocol from:
  http://www.nature.com/doifinder/10.1038/nn.3920

blocks of 100s for gratings drifting at 1cycle/s but refreshed only @ 2Hz
                    --> phase reversing 

** August 12th 2026 **
  --> modified to be better suited to the response in 2P
    we struggled to osberve responses later than 10s after stimulus onset
        --> we end up analyzing only onset dynamics
            --> we want more onsets
                --> we replace blocks of 100s by 10 blocks of 10s
"""
import os
import itertools

Screen="Dell-2020"

def build_movie(X, name='temp', rm=True):
  with open('%s.json' % name, 'w') as f:
    f.write(X)
  os.system('cd physion/src; python -m physion.visual_stim.build ../../%s.json; cd ../..' % name)
  if rm:
    os.remove('%s.json' % name)

def GratingPhaseReversing(Orientation=45., # deg.
                          Screen="Dell-2020", 
                          Nrepeat=100, 
                          interstim=4.,
                          jitter=2.5,
                          Duration=10.0):
  return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "grating",
    "Screen": "%s",
    "movie_refresh_freq": 2.0,
    "-----------------------------------------------------------------1":0,
    "presentation-duration": %.1f,
    "presentation-interstim-period": %.1f,
    "presentation-interstim-jitter": %.1f,
    "presentation-prestim-period": 20.0,
    "presentation-poststim-period": 20.0,
    "presentation-blank-screen-color": 0.5,
    "N-repeat": %i,
    "-----------------------------------------------------------------3":0,
    "angle": %.1f,
    "speed": 1.0,
    "spatial-freq":0.05, 
    "screen-color": 1.0
  }
  """ % (Screen, Duration, interstim, jitter, Nrepeat, Orientation)

def MixedNovelFamiliar(NovelOrientation=135.,
                       FamiliarOrientation=45., # deg.
                       Screen="Dell-2020", 
                       Nrepeat=100, 
                       Duration=10.0,
                       interstim=5.,
                       jitter=2.):
   
  mixed = """{
    "Presentation": "multiprotocol",
    "shuffling" :"full",
    "shuffling-seed" :34,
    "movie_refresh_freq":2.0,
    "units":"cm",
    "presentation-interstim-period": %.1f,
    "presentation-interstim-jitter": %.1f,
    "presentation-prestim-period": 20.0,
    "presentation-poststim-period": 20.0,
    "presentation-blank-screen-color": 0.5,
    "Screen": "%s",
  """ % (interstim, jitter, Screen)

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
  build_movie(GratingPhaseReversing(Orientation=45.0, Screen=Screen, 
                                    # Nrepeat=100, 
                                    Nrepeat=2, 
                                    Duration=5., interstim=5, jitter=3), 
              name='Learning-Familiar-Grating-45deg-v2P')#, rm=False)
  build_movie(MixedNovelFamiliar(NovelOrientation=135.0, FamiliarOrientation=45.0, Screen=Screen, 
                                 Nrepeat=2, 
                                 Duration=5.0, interstim=5, jitter=3.), 
              name='Testing-Novel-Familiar-Grating-135deg-45deg-v2P')#, rm=False)