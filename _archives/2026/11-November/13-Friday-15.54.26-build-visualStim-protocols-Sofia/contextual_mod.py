#!/usr/bin/env python
"""
Contextual-modulation protocol of Sofia (from visualStim-protocols-BEFORE/Sofia):
    - contextual-mod

the sub-protocol files of the former protocol are lost
    ("subprotocols/surround-sup/*.json", "subprotocols/NDNF-NEW/*.json"),
    their parameters are rebuilt from its visual-stim.npy

    same episodes (parameters, index, repeat) as the former protocol, but the
    inter-stimulus periods between sub-protocols follow the current physion:
    from episode 10 on, the episodes start 2s earlier than in the former protocol
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_movie import build_movie

Screen = "Dell-2020"

# common settings of the sub-protocols
SUB = {"Presentation": "Stimuli-Sequence",
       "Stimulus": "grating",
       "Screen": Screen,
       "units": "cm",
       "movie_refresh_freq": 30.0,
       "presentation-duration": 1,
       "presentation-blank-screen-color": 0.5,
       "x-center": 0.0, "y-center": 0.0,
       "spatial-freq": 0.04,
       "contrast": 1.0}

# full-field drifting surround
SURROUND = {"radius-surround": 200.0, "speed-surround": 2.0,
            "spatial-freq-surround": 0.04, "phase-surround": 0.0,
            "contrast-surround": 1.0}

SUBPROTOCOLS = [
    # surround suppression: drifting patches
    ('center-big.json',
        {**SUB, "radius": 40.0, "angle": 0.0, "speed": 2, "phase": 90.0,
         "presentation-interstim-period": 2, "N-repeat": 2}),
    ('center-small.json',
        {**SUB, "radius": 20.0, "angle": 0.0, "speed": 2, "phase": 90.0,
         "presentation-interstim-period": 1, "N-repeat": 2}),
    # cross-orientation facilitation: patch + iso/cross surround
    ('cross-ori-fac.json',
        {**SUB, "radius": 20.0, "angle": 0.0, "speed": 2, "phase": 0.0, **SURROUND,
         "angle-surround-1": 0.0, "angle-surround-2": 90.0, "N-angle-surround": 2,
         "presentation-interstim-period": 1, "N-repeat": 1}),
    # inverse response: blank center (contrast 0) + iso/cross surround
    ('inverse-resp.json',
        {**SUB, "contrast": 0.0, "angle": 0.0, "speed": 0, "phase": 90.0, **SURROUND,
         "radius-1": 20.0, "radius-2": 40.0, "N-radius": 2,
         "angle-surround-1": 0.0, "angle-surround-2": 90.0, "N-angle-surround": 2,
         "presentation-interstim-period": 1, "N-repeat": 1}),
    # mismatch: slowly rotating full-field grating (control) vs. a fixed one (test)
    ('mismatch-resp-control.json',
        {**SUB, "radius": 200.0, "speed": 2, "phase": 0.0,
         "angle-1": 0.0, "angle-2": 11.25, "N-angle": 8,
         "presentation-interstim-period": 2, "N-repeat": 1}),
    #   (as in the former protocol: 8 conditions with the same angle, 1 repeat)
    ('mismatch-resp-test.json',
        {**SUB, "radius": 200.0, "speed": 2, "phase": 0.0,
         "angle-1": 0.0, "angle-2": 0.0, "N-angle": 8,
         "presentation-interstim-period": 2, "N-repeat": 1}),
]


def ContextualMod(Screen=Screen):
    """ returns the multiprotocol json and the {filename: json} of its sub-protocols """
    mod = {
        "Presentation": "multiprotocol",
        "Screen": Screen,
        "shuffling": "no",
        "shuffling-seed": 34,
        "movie_refresh_freq": 30.0,
        "units": "cm",
        "presentation-prestim-period": 1.0,
        "presentation-poststim-period": 1.0,
        "presentation-interstim-period": 1.0,
        "presentation-blank-screen-color": 0.5}
    for i, (filename, protocol) in enumerate(SUBPROTOCOLS, start=1):
        mod['Protocol-%i' % i] = filename
    return json.dumps(mod, indent=4),\
        {filename: json.dumps(protocol, indent=4) for filename, protocol in SUBPROTOCOLS}


if __name__ == '__main__':

    protocol, subprotocols = ContextualMod()
    build_movie(protocol, name='contextual-mod', subprotocols=subprotocols)
