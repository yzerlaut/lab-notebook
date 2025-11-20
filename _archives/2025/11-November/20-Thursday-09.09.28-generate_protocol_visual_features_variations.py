# 
import itertools

Screen="Dell-2020-low-resolution"
Saccade_Amplitude = '50.0' # 200.0

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
  "Screen": "%s",
""" % Screen

Nrepeat = 15 

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
  "_______________________________________________________________________2":0,
  "Image-ID-1": 0, "Image-ID-2": 3, "N-Image-ID": 2,
  "Screen": "%s"
}""" % (Nrepeat, Saccade_Amplitude, contrast, size, Screen)
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
  "_______________________________________________________________________2":0,
  "Image-ID-1": 0, "Image-ID-2": 3, "N-Image-ID": 2,
  "Screen": "%s"
}""" % (Nrepeat, contrast, size, Screen)
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
  "spatial-freq":0.04,
  "_______________________________________________________________________2":0,
  "angle-1": 0, "angle-2": 90, "N-angle": 2,
  "Screen": "%s"
}""" % (Nrepeat, contrast, size, Screen)
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
  "spatial-freq":0.04,
  "_______________________________________________________________________2":0,
  "angle-1": 0, "angle-2": 90, "N-angle": 2,
  "Screen": "%s"
}""" % (Nrepeat, Saccade_Amplitude, contrast, size, Screen)
    else:
        print('protocol not recognized !!')
        protocol = ''

    return protocol 

i = 1 # protocol counter

for spatial, temporal, contrast, size in itertools.product(\
   ['low', 'high'], ['low', 'high'], [0.2, 1.0], [25., 300.]):
    protocol = single_protocol(spatial, temporal, contrast, size) 
    if protocol!='':
        with open('protocol-%i.json' % i, 'w') as f:
            f.write(protocol)
    multiprotocol += '  "Protocol-%i": "protocol-%i.json",\n' % (i, i)
    i += 1

multiprotocol = multiprotocol[:-2]+'}'

with open('full-protocol.json', 'w') as f:
    f.write(multiprotocol)

