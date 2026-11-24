#!/usr/bin/env python
"""Orientation and contrast tuning protocol for Sally, with optogenetic silencing.

Static gratings, Radius=60 degree, in 3 sub-protocols:

| sub-protocol       | orientations            | contrasts                 | repeats                 |
| orientation tuning | 8 (0, 22.5, ..., 157.5) | 0.2                       | 20 (10 blank + 10 opto) |
| orientation tuning | 8 (0, 22.5, ..., 157.5) | 1.0                       | 20 (10 blank + 10 opto) |
| contrast tuning    | 0                       | 8, log-spaced, 0.05 - 1.0 | 20 (10 blank + 10 opto) |

Duration 1s, Interstim = 4s with Jitter = 1s

Optogenetic silencing on the odd trials (odd repeats of each stimulus: 10 of the 20 repeats),
from OPTO_PRE_WINDOW before the stimulus onset to OPTO_POST_WINDOW after its offset
(physion "Opto-stim", TTL on the 'LED-optogenetics-activation' NIdaq line)
"""

import sys
import os
import json
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_movie import build_movie

# Screen="Dell-2020-low-resolution"
# Screen="LN-VR-3screens"
Screen = "LN-2screens"

Spatial_Freq = 0.04  # cycle/degree

# stimulus radius (degrees)
RADIUS = 60.

# orientation tuning: N_ANGLE orientations at each of these contrasts
N_ANGLE = 8
ANGLE_MIN, ANGLE_MAX = 0., 157.5
TUNING_CONTRASTS = [0.2, 1.0]

# contrast tuning: N_CONTRAST log-spaced contrasts at this orientation
N_CONTRAST = 8
CONTRAST_MIN, CONTRAST_MAX = 0.05, 1.0
CONTRAST_CURVE_ANGLE = 0.

Presentation_Duration = 1.0
Interstim = 4.0
Jitter = 1.0

# optogenetic silencing: trials ('all', 'odd' or 'even' repeats) and light window around the stimulus (s)
#   3s of light per trial, on one trial out of two (alternating even and odd repeats)
OPTO_TRIALS = 'odd'
OPTO_PRE_WINDOW = 1.0
OPTO_POST_WINDOW = 1.0

x = 45.
y = 20.


def MT(Screen, Nrepeat, x, y):
    """
    Mixed orientation and contrast tuning protocol, with optogenetic silencing.
        returns the multiprotocol json and the {filename: json} of its sub-protocols
    """

    mixedTuning = """{
    "Presentation": "multiprotocol",
    "shuffling":"full-with-alternate-even-odd-repeats",
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

    def single_protocol(variation):
        protocol = """{
    "Presentation": "Stimulus-Sequence",
    "Stimulus": "grating",
    "presentation-duration": %.1f,
    "presentation-interstim-period": %.1f,
    "N-repeat": %i,
    "_______________________________________________________________________1":0,
    "radius": %.2f,
    "x-center": %.2f,
    "y-center": %.2f,
    "spatial-freq": %.3f,
    "_______________________________________________________________________2":0,
    %s,
    "Screen": "%s"
  }""" % (Presentation_Duration, Interstim, Nrepeat, RADIUS, x, y,
         Spatial_Freq, variation, Screen)
        return protocol

    def angle_variation(contrast):
        return """"contrast": %.2f,
    "angle-1": %.1f,
    "angle-2": %.1f,
    "N-angle": %i""" % (contrast, ANGLE_MIN, ANGLE_MAX, N_ANGLE)

    def contrast_variation(angle):
        return """"angle": %.1f,
    "contrast-1": %.2f,
    "contrast-2": %.2f,
    "N-log-contrast": %i""" % (angle, CONTRAST_MIN, CONTRAST_MAX, N_CONTRAST)

    # the protocol name of the episodes gives the curve
    subprotocols = {}
    for contrast in TUNING_CONTRASTS:
        name = 'orientation-tuning_contrast=%.1f.json' % contrast
        subprotocols[name] = single_protocol(angle_variation(contrast))
    name = 'contrast-curve_angle=%.0f.json' % CONTRAST_CURVE_ANGLE
    subprotocols[name] = single_protocol(contrast_variation(CONTRAST_CURVE_ANGLE))

    for i, name in enumerate(subprotocols, start=1):
        mixedTuning += '  "Protocol-%i": "%s",\n' % (i, name)

    # optogenetic silencing on the OPTO_TRIALS repeats of all sub-protocols
    opto = {"pre_window": OPTO_PRE_WINDOW, "post_window": OPTO_POST_WINDOW,
            **{"Protocol-%i" % k: {"trials": OPTO_TRIALS}
               for k in range(1, len(subprotocols) + 1)}}
    mixedTuning += '  "Opto-stim": %s,\n' % json.dumps(opto)

    mixedTuning = mixedTuning[:-2] + '}'

    return mixedTuning, subprotocols


if __name__ == '__main__':
    tic = time.time()
    x, y = 45, 20
    Nrepeat = 20
    protocol, subprotocols = MT(Screen, Nrepeat, x, y)
    build_movie(protocol, name='mixed-tuning-contrast-wOPTO-x=%.0f-z=%.0f' % (x, y),
                subprotocols=subprotocols)
    print(' --> protocol generation took %.1f minutes ' % ((time.time() - tic) / 60.))
