#!/usr/bin/env python
"""
Background-luminance blocks with optogenetic activation, protocol for Sally.

Multiprotocol, sequential (no shuffling): 4 blocks of 5 minutes, one per
background luminance, in the order 0, 0.5, 0.25, 0.75.
In each block, optogenetic activations of increasing duration:
    10 x 1s, then 10 x 3s, then 10 x 5s
with the same interstim interval between all of them (7s), so the 1s
sequence is shorter than the 5s one.

Each activation is a "uniform_bg" episode at the block luminance (i.e. no
visual change) with the optogenetic stimulation over the whole episode
(no pre/post window): one subprotocol per (luminance, duration), 12 in total.

The interstim luminance follows the block (physion multiprotocol key
"interstim-color-from-subprotocols"); it switches halfway between the last
episode of a block and the first one of the next.

Timeline of a block (300s):
    3.5s blank | 10 x [1s + 7s] | 10 x [3s + 7s] | 10 x [5s + 7s], last blank cut to 3.5s
    (the first block starts after the 3.5s prestim)

run from the root of the repository (as the other scripts of this folder):
    uv run python build-visualStim-protocols-Sally/bg_luminance_opto.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_movie import build_movie

# Screen="Dell-2020-low-resolution"
# Screen="LN-VR-3screens"
Screen = "LN-2screens"

LUMINANCES = [0., 0.5, 0.25, 0.75]   # block order
BLOCK_DURATION = 5*60.               # s, per luminance
OPTO_DURATIONS = [1., 3., 5.]        # s, in this order within each block
N_REPEAT = 10                        # per opto duration
OPTO_PRE, OPTO_POST = 0., 0.         # s, opto window beyond the episode

# same interstim for all episodes, filling the block:
#   BLOCK_DURATION = N_REPEAT*sum(OPTO_DURATIONS) + N_episodes*INTERSTIM
INTERSTIM = (BLOCK_DURATION-N_REPEAT*sum(OPTO_DURATIONS))/\
                (N_REPEAT*len(OPTO_DURATIONS))  # 7s


def subprotocol(Screen, luminance, duration):
    """ N_REPEAT episodes of "duration", uniform background at "luminance" """
    return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "uniform_bg",
    "Screen": "%s",
    "shuffling": "none",
    "-----------------------------------------------------------------1":0,
    "presentation-duration": %.1f,
    "presentation-interstim-period": %.1f,
    "presentation-blank-screen-color": %.2f,
    "N-repeat": %i,
    "-----------------------------------------------------------------2":0,
    "screen-color": %.2f
  }
  """ % (Screen, duration, INTERSTIM, luminance, N_REPEAT, luminance)


def BLO(Screen, name):
    """ Background-Luminance blocks + Opto multiprotocol """
    SUBPROTOCOLS = [(lum, dur) for lum in LUMINANCES for dur in OPTO_DURATIONS]

    protocol = """{
    "Presentation": "multiprotocol",
    "shuffling": "none",
    "interstim-color-from-subprotocols": true,
    "movie_refresh_freq": 10.0,
    "units": "cm",
    "presentation-prestim-period": %.1f,
    "presentation-poststim-period": %.1f,
    "presentation-interstim-period": %.1f,
    "presentation-blank-screen-color": %.2f,
    "Screen": "%s",
    "-----------------------------------------------------------------1":0,
    "Opto-stim": {
        "pre_window": %.1f,
        "post_window": %.1f,
%s
    },
    "-----------------------------------------------------------------2":0,
""" % (INTERSTIM/2., INTERSTIM/2., INTERSTIM, LUMINANCES[0], Screen,
       OPTO_PRE, OPTO_POST,
       ',\n'.join('        "Protocol-%i": {"trials": "all"}' % (i+1)
                  for i in range(len(SUBPROTOCOLS))))

    subprotocols = {}  # {filename: json}, written next to the protocol by build_movie
    for i, (lum, dur) in enumerate(SUBPROTOCOLS):
        filename = 'uniform-bg-lum-%.2f-opto-%.0fs.json' % (lum, dur)
        subprotocols[filename] = subprotocol(Screen, lum, dur)
        protocol += '    "Protocol-%i": "%s",\n' % (i+1, filename)

    return protocol[:-2]+'\n}\n', subprotocols


if __name__ == '__main__':
    name = 'bg-luminance-opto'
    protocol, subprotocols = BLO(Screen, name)
    build_movie(protocol, name=name, subprotocols=subprotocols)
