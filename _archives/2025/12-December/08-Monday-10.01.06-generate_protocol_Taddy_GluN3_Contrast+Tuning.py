# 
import itertools

multiprotocol = """{
  "Presentation": "multiprotocol",
  "shuffling" :"full",
  "shuffling-seed" :34,
  "movie_refresh_freq":30.0,
  "units":"cm",
  "presentation-prestim-period": 5.0,
  "presentation-poststim-period": 5.0,
  "presentation-interstim-period": 3.0,
  "presentation-blank-screen-color": 0.5,
  "Screen": "Dell-2020",
"""


contrast_sensitivity = """
{
  "Presentation": "Stimuli-Sequence",
  "Stimulus": "grating",
  "Screen": "Dell-2020",
  "shuffling-seed": 1,
  "units":"lin-deg",
  "------------------------------------------------------------------------1":0,
  "presentation-duration": 2,
  "presentation-interstim-period": 3,
  "presentation-blank-screen-color": 0.5,
  "N-repeat": 10,
  "------------------------------------------------------------------------2":0,
  "contrast-1": 0.05, "contrast-2": 1.0, "N-contrast": 8,
  "------------------------------------------------------------------------3":0,
  "angle": 0,
  "speed": 0,
  "spatial-freq": 0.04,
  "radius": 200,
  "phase": 90.0
}

"""

tunings = ["""
{
  "Presentation": "Stimuli-Sequence",
  "Stimulus": "grating",
  "Screen": "Dell-2020",
  "shuffling-seed": 1,
  "units":"lin-deg",
  "------------------------------------------------------------------------1":0,
  "presentation-duration": 2,
  "presentation-interstim-period": 3,
  "presentation-blank-screen-color": 0.5,
  "N-repeat": 10,
  "------------------------------------------------------------------------2":0,
  "angle-1": 0.0, "angle-2": 157.5, "N-angle": 8,
  "------------------------------------------------------------------------3":0,
  "contrast": %.2f,
  "speed": 0,
  "spatial-freq": 0.04,
  "radius": 200,
  "phase": 90.0
}
""" % contrast for contrast in [0.2, 0.5, 1.0]]

i = 1 # protocol counter

for protocol in tunings+[contrast_sensitivity]:
    with open('protocol-%i.json' % i, 'w') as f:
        f.write(protocol)
    multiprotocol += '  "Protocol-%i": "protocol-%i.json",\n' % (i, i)
    i += 1

multiprotocol = multiprotocol[:-2]+'}'

with open('mixed-Tuning-Contrast-selectivity.json', 'w') as f:
    f.write(multiprotocol)

