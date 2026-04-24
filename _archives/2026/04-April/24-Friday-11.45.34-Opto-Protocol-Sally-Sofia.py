import os
import itertools

Screen="LN-2screens"

def build_movie(X, name='temp', rm=True):
  with open('%s.json' % name, 'w') as f:
    f.write(X)
  os.system('cd physion/src; python -m physion.visual_stim.build ../../%s.json; cd ../..' % name)
  if rm:
    os.remove('%s.json' % name)


#################################################################
###   full-field grating 2 contrasts 4 directions opto/blank  ###
#################################################################

def FF(Screen, Nrepeat):
  return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "grating",
    "Screen": "%s",
    "shuffling": "full-with-alternate-even-odd-repeats",
    "-------                 --> we photostimulate on odd trials ! ----": 0,
    "shuffling-seed": 34,
    "-----------------------------------------------------------------1": 0,
    "presentation-duration": 2.0,
    "presentation-interstim-period": 6.0,
    "N-repeat": %i,
    "-----------------------------------------------------------------2": 0,
    "angle-1": 0.0,
    "angle-2": 270.0,
    "N-angle": 4,
    "contrast-1": 0.4,
    "contrast-2": 1.0,
    "N-contrast": 2,
    "-----------------------------------------------------------------3": 0,
    "spatial-freq": 0.06,
    "speed": 1,
    "radius": 400,
    "json_location": "./",
    "presentation-prestim-period": 6,
    "presentation-poststim-period": 6,
    "presentation-blank-screen-color": 0.5,
    "movie_refresh_freq": 30.0,
    "units": "cm"
  }
  """ % (Screen, Nrepeat)

####################################################################
###      grey screen protocol with opto of various durations     ###
####################################################################

def GS(Screen, Nrepeat):
   
  greyScreen_wOpto = """{
    "Presentation": "multiprotocol",
    "shuffling": "full-with-alternate-even-odd-repeats",
    "shuffling-seed" :34,
    "movie_refresh_freq":30.0,
    "units":"cm",
    "presentation-prestim-period": 15.0,
    "presentation-poststim-period": 5.0,
    "presentation-interstim-period": 3.0,
    "presentation-blank-screen-color": 0.5,
    "Screen": "%s",
  """ % Screen

  def single_protocol(Screen, Duration, Nrepeat):
    return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "uniform_bg",
    "Screen": "%s",
    "-----------------------------------------------------------------1":0,
    "presentation-duration": %.2f,
    "presentation-interstim-period": 5.0,
    "presentation-blank-screen-color": 0.25,
    "N-repeat": %i,
    "-----------------------------------------------------------------3":0,
    "screen-color": 0.5
  }
  """ % (Screen, Duration, Nrepeat)

  i = 1 # protocol counter
  for Duration in [1., 2., 3., 5., 7.]:
      protocol = single_protocol(Screen, Duration, Nrepeat)
      with open('protocol-%i.json' % i, 'w') as f:
        f.write(protocol)
      greyScreen_wOpto += '  "Protocol-%i": "protocol-%i.json",\n' % (i, i)
      i += 1

  greyScreen_wOpto = greyScreen_wOpto[:-2]+'}'

  return greyScreen_wOpto



if 1:
  build_movie(FF(Screen, 20), name='ffDG-4dir-2ctrst+1sPrePostOpto')
  build_movie(GS(Screen, 20), name='greyScreen-varDuration+0sPrePostOpto')
