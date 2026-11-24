#!/usr/bin/env python
"""Neurometric task protocol for Sally: decoding the orientation of static gratings.

Orientations over a 20 degree range (7 points), in 4 configurations, with mean orientations
45 degrees apart (180/4) so that no orientation is repeated across configurations:

| stimulus                       | orientations              | repeats |
| Radius=70 degree, Contrast=0.3 | 7 over 20 deg, around 0   | 10      |
| Radius=70 degree, Contrast=1.0 | 7 over 20 deg, around 45  | 10      |
| Radius=15 degree, Contrast=0.3 | 7 over 20 deg, around 90  | 10      |
| Radius=15 degree, Contrast=1.0 | 7 over 20 deg, around 135 | 10      |

Duration 1s, Interstim = 2s with Jitter = 1s
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

from build_movie import build_movie

# Screen="Dell-2020-low-resolution"
# Screen="LN-VR-3screens"
Screen = "LN-2screens"

# orientations: N_ANGLE points over ANGLE_RANGE degrees, around the mean orientation of the configuration
ANGLE_RANGE = 20.
N_ANGLE = 7
ANGLES = np.linspace(-ANGLE_RANGE / 2., ANGLE_RANGE / 2., N_ANGLE)

Spatial_Freq = 0.04  # cycle/degree

# stimulus radius (degrees)
RADIUS_LARGE = 70.
RADIUS_SMALL = 15.

# (radius in degrees, contrast, mean orientation in degrees)
#   mean orientations 180/4 = 45 degrees apart: no orientation shared by two configurations
STIMULI = [
    (RADIUS_LARGE, 0.3, 0.),
    (RADIUS_LARGE, 1.0, 45.),
    (RADIUS_SMALL, 0.3, 90.),
    (RADIUS_SMALL, 1.0, 135.),
]

Presentation_Duration = 1.0
Interstim = 2.0
Jitter = 1.0

x = 45.
y = 20.


def protocol_name(radius, contrast, angle):
    return 'grating_radius=%.0f_contrast=%.1f_angle=%.1f.json' % (radius, contrast, angle)


def NT(Screen, Nrepeat, x, y):
    """
    Neurometric task protocol (gratings).
        returns the multiprotocol json and the {filename: json} of its sub-protocols
    """

    neurometricTask = """{
    "Presentation": "multiprotocol",
    "shuffling":"full",
    "shuffling-seed":34,
    "movie_refresh_freq":10.0,
    "units":"cm",
    "presentation-prestim-period": 15.0,
    "presentation-poststim-period": 5.0,
    "presentation-interstim-period": %.1f,
    "presentation-interstim-jitter": %.1f,
    "presentation-blank-screen-color": 0.5,
    "Screen": "%s",
  """ % (Interstim, Jitter, Screen)

    def single_protocol(radius, contrast, angle):
        protocol = """{
    "Presentation": "Stimulus-Sequence",
    "Stimulus": "grating",
    "presentation-duration": %.1f,
    "presentation-interstim-period": %.1f,
    "N-repeat": %i,
    "_______________________________________________________________________1":0,
    "contrast": %.2f,
    "radius": %.2f,
    "x-center": %.2f,
    "y-center": %.2f,
    "spatial-freq": %.3f,
    "_______________________________________________________________________2":0,
    "angle": %.3f,
    "Screen": "%s"
  }""" % (Presentation_Duration, Interstim, Nrepeat, contrast, radius, x, y,
         Spatial_Freq, angle, Screen)
        return protocol

    # one sub-protocol per stimulus, named after it ("grating_radius=15_contrast=0.3_angle=83.3.json"):
    #   the protocol name of the episodes gives the configuration and the orientation
    subprotocols = {}
    i = 1  # protocol counter
    for radius, contrast, center in STIMULI:
        for angle in (center + ANGLES) % 180:
            name = protocol_name(radius, contrast, angle)
            subprotocols[name] = single_protocol(radius, contrast, angle)
            neurometricTask += '  "Protocol-%i": "%s",\n' % (i, name)
            i += 1

    neurometricTask = neurometricTask[:-2] + '}'

    return neurometricTask, subprotocols


if __name__ == '__main__':
    tic = time.time()
    x, y = 45, 20
    Nrepeat = 10
    protocol, subprotocols = NT(Screen, Nrepeat, x, y)
    build_movie(protocol, name='task-gratingAngle-x=%.0f-z=%.0f' % (x, y),
                subprotocols=subprotocols)
    print(' --> protocol generation took %.1f minutes ' % ((time.time() - tic) / 60.))
