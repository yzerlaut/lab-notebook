#!/usr/bin/env python
"""Rough Mapping protocol for Sally."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_movie import build_movie

# Screen="Dell-2020-low-resolution"
# Screen="LN-VR-3screens"
Screen = "LN-2screens"


def RM(Screen, Nrepeat):
    """Rough Mapping protocol."""
    return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "grating",
    "movie_refresh_freq":10.0,
    "Screen": "%s",
    "-----------------------------------------------------------------1":0,
    "presentation-duration": 1,
    "presentation-interstim-period": 1.5,
    "N-repeat": %i,
    "-----------------------------------------------------------------2":0,
    "x-center-1": 15.0, "x-center-2": 75.0, "N-x-center": 3,
    "y-center-1": 0.0, "y-center-2": 40.0, "N-y-center": 3,
    "-----------------------------------------------------------------3":0,
    "spatial-freq": 0.06,
    "y-center":0.0,
    "speed":2,
    "angle": 0,
    "radius": 15
  }
  """ % (Screen, Nrepeat)


if __name__ == '__main__':
    Nrepeat = 20
    build_movie(RM(Screen, Nrepeat), name='rough-mapping')
