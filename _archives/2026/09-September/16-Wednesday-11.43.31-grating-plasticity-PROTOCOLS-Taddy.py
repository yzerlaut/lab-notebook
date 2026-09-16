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
import os, subprocess

Screen="Dell-2020"

def build_movie(X, name='temp', rm=True):

  with open('%s.json' % name, 'w') as f:
    f.write(X)

  p = subprocess.Popen('python -m physion.visual_stim.build ../../%s.json' % name,
                   cwd=os.path.join('.', 'physion', 'src'))
  p.wait()

  if rm:
    os.remove('%s.json' % name)

def GratingPhaseReversing(Orientation=45., # deg.
                          Screen="Dell-2020", 
                          Nrepeat=100, 
                          flicker_freq=2.,
                          interstim=4.,
                          jitter=2.5,
                          Duration=10.0):
  return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "grating",
    "Screen": "%s",
    "movie_refresh_freq": %.1f,
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
    "speed": %.1f,
    "spatial-freq":0.05, 
    "screen-color": 1.0
  }
  """ % (Screen, flicker_freq, 
         Duration, interstim, jitter, Nrepeat, 
         Orientation,
         flicker_freq/2.)

def MixedNovelFamiliar(NovelOrientation=135.,
                       FamiliarOrientation=45., # deg.
                       Screen="Dell-2020", 
                       flicker_freq=2.,
                       Nrepeat=100, 
                       Duration=10.0,
                       interstim=5.,
                       jitter=2.):
   
  mixed = """{
    "Presentation": "multiprotocol",
    "shuffling" :"full",
    "shuffling-seed" :34,
    "movie_refresh_freq":%.1f,
    "units":"cm",
    "presentation-interstim-period": %.1f,
    "presentation-interstim-jitter": %.1f,
    "presentation-prestim-period": 20.0,
    "presentation-poststim-period": 20.0,
    "presentation-blank-screen-color": 0.5,
    "Screen": "%s",
  """ % (flicker_freq, interstim, jitter, Screen)

  i = 1 # protocol counter
  for Orientation in [FamiliarOrientation, NovelOrientation]:
      protocol = GratingPhaseReversing(Orientation=Orientation, 
                                       Screen=Screen, 
                                       Nrepeat=Nrepeat, 
                                       Duration=Duration,
                                       flicker_freq=flicker_freq)
      if protocol!='':
          with open('protocol-%i.json' % i, 'w') as f:
              f.write(protocol)
      mixed += '  "Protocol-%i": "protocol-%i.json",\n' % (i, i)
      i += 1

  mixed = mixed[:-2]+'}'

  return mixed 


if 0:
  # original Cooke et al.,
  build_movie(GratingPhaseReversing(Orientation=45.0, Screen=Screen, 
                                    flicker_freq=2., 
                                    Nrepeat=10, 
                                    Duration=100., interstim=30, jitter=3), 
              name='Learning-Familiar-Grating-45deg')#, rm=False)
  build_movie(MixedNovelFamiliar(NovelOrientation=135.0, FamiliarOrientation=45.0, Screen=Screen, 
                                 flicker_freq=2., 
                                 Nrepeat=10, 
                                 Duration=100., interstim=30, jitter=3), 
              name='Testing-Novel-Familiar-Grating-135deg-45deg')#, rm=False)
  # v2P, 100 blocks of 5s
  build_movie(GratingPhaseReversing(Orientation=45.0, Screen=Screen, 
                                    flicker_freq=2., 
                                    Nrepeat=100, 
                                    Duration=5., interstim=5, jitter=3), 
              name='Learning-Familiar-Grating-45deg-v2P')#, rm=False)
  build_movie(MixedNovelFamiliar(NovelOrientation=135.0, FamiliarOrientation=45.0, Screen=Screen, 
                                 flicker_freq=2., 
                                 Nrepeat=100, 
                                 Duration=5.0, interstim=5, jitter=3.), 
              name='Testing-Novel-Familiar-Grating-135deg-45deg-v2P')#, rm=False)
  # Kim et al., 2020
  build_movie(GratingPhaseReversing(Orientation=45.0, Screen=Screen, 
                                    flicker_freq=0.5, 
                                    Nrepeat=5, 
                                    Duration=120., 
                                    interstim=30, jitter=3), 
              name='Learning-Familiar-Grating-45deg-Kim2020')#, rm=False)
  build_movie(MixedNovelFamiliar(NovelOrientation=135.0, FamiliarOrientation=45.0, Screen=Screen, 
                                 flicker_freq=0.5, 
                                 Nrepeat=5, 
                                 Duration=120., 
                                 interstim=30, jitter=3.), 
              name='Testing-Novel-Familiar-Grating-135deg-45deg-Kim2020')#, rm=False)
if 1:
  # Kim et al., 2020 - shifted by 45deg.
  build_movie(GratingPhaseReversing(Orientation=0.0, Screen=Screen, 
                                    flicker_freq=0.5, 
                                    Nrepeat=5, 
                                    Duration=120., 
                                    interstim=30, jitter=3), 
              name='Learning-Familiar-Grating-0deg-Kim2020')#, rm=False)
  build_movie(MixedNovelFamiliar(NovelOrientation=90.0, FamiliarOrientation=0.0, Screen=Screen, 
                                 flicker_freq=0.5, 
                                 Nrepeat=5, 
                                 Duration=120., 
                                 interstim=30, jitter=3.), 
              name='Testing-Novel-Familiar-Grating-90deg-0deg-Kim2020')#, rm=False)
