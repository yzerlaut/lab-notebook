#!/usr/bin/env python
"""Timing precision protocol for Sally: sensitivity to the timing of the saccades of a virtual scene exploration.

Saccades at 2 Hz on a regular grid, each moved earlier or later by a number of frames,
log-spaced across conditions (60 Hz movie):

    saccade-jitter-frames   0 (regular), 2, 4, 7, 12
    jitter                  0, 33, 67, 117, 200 ms

| stimulus                       | pairs | image pairs | repeats |
| Radius=60 degree, Contrast=0.3 | 2     | 1-15, 86-99 | 10      |
| Radius=60 degree, Contrast=1.0 | 2     | 10-96, 7-29 | 10      |

The two images of a pair share the same jitter seed: only the image differs between them.
Same sequence of shifts for all conditions: only the timing differs.

Duration 4s, Interstim = 1s without jitter: the episodes start on a movie frame
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

from build_movie import build_movie, NI_FOLDER

# Screen="Dell-2020-low-resolution"
# Screen="LN-VR-3screens"
Screen = "LN-2screens"

# visual angle of one image pixel (Allen images: 1174x918 pixels)
#   0.134 deg: as when the images are stretched over the Dell-2020 screen
#   (the geometry of the pair selection)
Degree_per_Pixel_of_Image = 0.134

# refresh rate of the movie (Hz): a multiple of the saccade rate
Refresh_Rate = 60.

# saccades
Regular_Saccade_Rate = 2.0 # in Hz
JITTER_FRAMES = np.concatenate([[0], # regular saccades
                                np.round(np.logspace(np.log(2), np.log(12), 4,
                                                     base=np.exp(1)), 0).astype(int)])
Saccade_Amplitude = 40.0 # in degrees
Shift_Seed = 0 # the shifts are the same in all conditions

# stimulus radius (degrees)
RADIUS = 60.

# (radius in degrees, contrast, [(image pair, seed of the jitter), ...])
STIMULI = [
    (RADIUS, 0.3, [('1-15', 0),  ('86-99', 1)]),
    (RADIUS, 1.0, [('10-96', 3), ('7-29', 4)]),
]

Presentation_Duration = 4.0
Interstim = 1.0

x = 45.
y = 20.


def TP(Screen, Nrepeat, x, y):
    """
    Timing precision protocol.
        returns the multiprotocol json and the {filename: json} of its sub-protocols
    """

    timingPrecision = """{
    "Presentation": "multiprotocol",
    "shuffling":"full",
    "shuffling-seed":34,
    "movie_refresh_freq":%.1f,
    "units":"cm",
    "presentation-prestim-period": 15.0,
    "presentation-poststim-period": 5.0,
    "presentation-interstim-period": %.1f,
    "presentation-blank-screen-color": 0.5,
    "Screen": "%s",
  """ % (Refresh_Rate, Interstim, Screen)

    def single_protocol(radius, contrast, image, jitter, seed):
        protocol = """{
    "Presentation": "Stimulus-Sequence",
    "Stimulus": "images-VSE",
    "presentation-duration": %.1f,
    "presentation-interstim-period": %.1f,
    "N-repeat": %i,
    "_______________________________________________________________________1":0,
    "regular-saccade-rate": %.2f,
    "saccade-jitter-frames": %i,
    "saccade-amplitude-deg": %.1f,
    "seed": %i,
    "saccade-shift-seed": %i,
    "contrast": %.2f,
    "radius": %.2f,
    "x-center": %.2f,
    "y-center": %.2f,
    "NI_FOLDER": "%s",
    "degree-per-pixel-of-image": %.3f,
    "_______________________________________________________________________2":0,
    "Image-ID-1": "%s.jpeg",
    "Screen": "%s"
  }""" % (Presentation_Duration, Interstim, Nrepeat,
         Regular_Saccade_Rate, jitter, Saccade_Amplitude, seed, Shift_Seed,
         contrast, radius, x, y,
         NI_FOLDER, Degree_per_Pixel_of_Image, image, Screen)
        return protocol

    # one sub-protocol per condition, named after it ("1-15_image=15_jitter=17frames.json"):
    #   the protocol name of the episodes gives the pair, the image and the jitter
    subprotocols = {}
    i = 1  # protocol counter
    for radius, contrast, pairs in STIMULI:
        for pair, seed in pairs:
            for image in pair.split('-'):
                for jitter in JITTER_FRAMES:
                    name = '%s_image=%s_jitter=%iframes.json' % (pair, image, jitter)
                    subprotocols[name] = single_protocol(radius, contrast, image, jitter, seed)
                    timingPrecision += '  "Protocol-%i": "%s",\n' % (i, name)
                    i += 1

    timingPrecision = timingPrecision[:-2] + '}'

    return timingPrecision, subprotocols


if __name__ == '__main__':
    tic = time.time()
    x, y = 45, 20
    Nrepeat = 10
    protocol, subprotocols = TP(Screen, Nrepeat, x, y)
    build_movie(protocol, name='task-imageTiming-x=%.0f-z=%.0f' % (x, y),
                subprotocols=subprotocols)
    print(' --> protocol generation took %.1f minutes ' % ((time.time() - tic) / 60.))
