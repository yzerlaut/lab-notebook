#!/usr/bin/env python
"""
Receptive-field mapping protocols of Cibele (from visualStim-protocols-BEFORE/Cibele):
    - quick-spatial-mapping:  3x3 drifting-grating patches
    - sparse-noise-20min

the former jsons omitted some settings, the physion defaults (unchanged since)
    are written explicitly here
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_movie import build_movie

Screen = "Dell-2020"


def QuickSpatialMapping(Nrepeat=4, Screen=Screen):
    return json.dumps({
        "Presentation": "Stimuli-Sequence",
        "Stimulus": "grating",
        "Screen": Screen,
        "units": "cm",
        "movie_refresh_freq": 30.0,
        "presentation-duration": 1,
        "presentation-prestim-period": 6,
        "presentation-poststim-period": 6,
        "presentation-interstim-period": 4,
        "presentation-blank-screen-color": 0.5,
        "N-repeat": Nrepeat,
        "x-center-1": -36.0, "x-center-2": 36.0, "N-x-center": 3,
        "y-center-1": -23.0, "y-center-2": 23.0, "N-y-center": 3,
        "spatial-freq": 0.06,
        "speed": 2,
        "angle": 0,
        "radius": 12}, indent=4)


def SparseNoise(Nrepeat=2400, Screen=Screen):
    """ 2400 x 0.5s = 20min """
    return json.dumps({
        "Presentation": "Stimuli-Sequence",
        "Stimulus": "sparse-noise",
        "Screen": Screen,
        "units": "cm",
        "movie_refresh_freq": 30.0,
        "presentation-duration": 0.45,
        "presentation-prestim-period": 2,
        "presentation-poststim-period": 2,
        "presentation-interstim-period": 0.05,
        "presentation-blank-screen-color": 0.5,
        "N-repeat": Nrepeat,
        "screen-width": 116,
        "screen-height": 84,
        "sparseness": 4,
        "black-white-ratio": 50,
        "seed": 1,
        "size": 6}, indent=4)


if __name__ == '__main__':

    build_movie(QuickSpatialMapping(), name='quick-spatial-mapping')

    build_movie(SparseNoise(), name='sparse-noise-20min')
