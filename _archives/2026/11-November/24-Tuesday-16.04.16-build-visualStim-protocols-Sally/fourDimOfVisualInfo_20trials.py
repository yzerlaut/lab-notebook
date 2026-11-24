#!/usr/bin/env python
"""Four-Dim of visual infos protocol for Sally."""

import sys
import os
import itertools
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_movie import build_movie, NI_FOLDER

# Screen="Dell-2020-low-resolution"
# Screen="LN-VR-3screens"
Screen = "LN-2screens"

# stimulus-center position:
Saccade_Amplitude = "40.0" # in degrees

# visual angle of one image pixel (Allen images: 1174x918 pixels)
#   0.134 deg: as when the images are stretched over the Dell-2020 screen
#   (the geometry of the pair selection)
Degree_per_Pixel_of_Image = 0.134

x = 45.
y = 20.


def FD(Screen, Nrepeat, x, y):
    """
    Four-Dim of visual infos protocol.
        returns the multiprotocol json and the {filename: json} of its sub-protocols
    """
    
    fourDimVisualInfo = """{
    "Presentation": "multiprotocol",
    "shuffling":"full",
    "shuffling-seed":34,
    "movie_refresh_freq":10.0,
    "units":"cm",
    "presentation-prestim-period": 15.0,
    "presentation-poststim-period": 5.0,
    "presentation-interstim-period": 3.0,
    "presentation-blank-screen-color": 0.5,
    "Screen": "%s",
  """ % Screen

    def single_protocol(spatial, temporal, contrast, size):
        if (spatial == 'high') and (temporal == 'high'):
            protocol = """{
    "Presentation": "Stimulus-Sequence",
    "Stimulus": "images-VSE",
    "presentation-duration": 4.0,
    "presentation-interstim-period": 3.0,
    "N-repeat": %i,
    "_______________________________________________________________________1":0,
    "min-saccade-duration": 0.2,
    "max-saccade-duration": 1.0,
    "saccade-amplitude-deg": %s,
    "seed": 0,
    "contrast": %.2f,
    "radius": %.2f,
    "x-center": %.2f,
    "y-center": %.2f,
    "NI_FOLDER": "%s",
    "degree-per-pixel-of-image": %.3f,
    "_______________________________________________________________________2":0,
    "Image-ID-1": "1.jpeg", "Image-ID-2": "4.jpeg",
    "Screen": "%s"
  }""" % (Nrepeat, Saccade_Amplitude, contrast, size, x, y,
         NI_FOLDER, Degree_per_Pixel_of_Image, Screen)
        elif (spatial == 'high') and (temporal == 'low'):
            protocol = """{
    "Presentation": "Stimulus-Sequence",
    "Stimulus": "images",
    "presentation-duration": 2.0,
    "presentation-interstim-period": 3.0,
    "N-repeat": %i,
    "_______________________________________________________________________1":0,
    "contrast": %.2f,
    "radius": %.2f,
    "x-center": %.2f,
    "y-center": %.2f,
    "NI_FOLDER": "%s",
    "degree-per-pixel-of-image": %.3f,
    "_______________________________________________________________________2":0,
    "Image-ID-1": "1.jpeg", "Image-ID-2": "4.jpeg",
    "Screen": "%s"
  }""" % (Nrepeat, contrast, size, x, y,
         NI_FOLDER, Degree_per_Pixel_of_Image, Screen)
        elif (spatial == 'low') and (temporal == 'low'):
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
        elif (spatial == 'low') and (temporal == 'high'):
            protocol = """{
    "Presentation": "Stimulus-Sequence",
    "Stimulus": "grating-VSE",
    "presentation-duration": 4.0,
    "presentation-interstim-period": 3.0,
    "N-repeat": %i,
    "_______________________________________________________________________1":0,
    "min-saccade-duration": 0.2,
    "max-saccade-duration": 1.0,
    "saccade-amplitude-deg": %s, 
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
  
    subprotocols = {}
    i = 1  # protocol counter
    for spatial, temporal, contrast, size in itertools.product(
        ['low', 'high'], ['low', 'high'], [0.2, 1.0], [15., 50.]):
        protocol = single_protocol(spatial, temporal, contrast, size) 
        if protocol != '':
            subprotocols['protocol-%i.json' % i] = protocol
        fourDimVisualInfo += '  "Protocol-%i": "protocol-%i.json",\n' % (i, i)
        i += 1

    fourDimVisualInfo = fourDimVisualInfo[:-2] + '}'

    return fourDimVisualInfo, subprotocols


if __name__ == '__main__':
    tic = time.time()
    x, y = 45, 20
    Nrepeat = 20
    protocol, subprotocols = FD(Screen, Nrepeat, x, y)
    build_movie(protocol, name='4dim-visInfo-x=%.0f-z=%.0f-FIX' % (x, y),
                subprotocols=subprotocols)
    print(' --> protocol generation took %.1f minutes ' % ((time.time() - tic) / 60.))
