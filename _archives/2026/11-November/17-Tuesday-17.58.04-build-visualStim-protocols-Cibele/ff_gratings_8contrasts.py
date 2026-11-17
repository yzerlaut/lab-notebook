#!/usr/bin/env python
"""
Full-field static gratings protocol of Cibele (from visualStim-protocols-BEFORE/Cibele):
    - ff-gratings-2orientations-8contrasts-15repeats
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_movie import build_movie

Screen = "Dell-2020"


def FFgratings(angles, contrasts, Nrepeat=15,
               Screen=Screen):
    return json.dumps({
        "Presentation": "Stimuli-Sequence",
        "Stimulus": "grating",
        "Screen": Screen,
        "units": "lin-deg",
        "movie_refresh_freq": 30.0,
        "shuffling-seed": 1,
        "presentation-duration": 2,
        "presentation-prestim-period": 4,
        "presentation-poststim-period": 4,
        "presentation-interstim-period": 4,
        "presentation-blank-screen-color": 0.5,
        "N-repeat": Nrepeat,
        "angle-1": angles[0], "angle-2": angles[1], "N-angle": angles[2],
        "contrast-1": contrasts[0], "contrast-2": contrasts[1], "N-contrast": contrasts[2],
        "speed": 0,
        "spatial-freq": 0.04,
        "radius": 200,
        "phase": 90.0}, indent=4)


if __name__ == '__main__':

    build_movie(FFgratings((0, 90, 2), (0.05, 1.0, 8)),
                name='ff-gratings-2orientations-8contrasts-15repeats')
