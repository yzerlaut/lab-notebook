#!/usr/bin/env python
"""Precise Mapping protocol for Sally."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_movie import build_movie

# Screen="Dell-2020-low-resolution"
# Screen="LN-VR-3screens"
Screen = "LN-2screens"


def PM(Screen, Nrepeat):
    """Precise Mapping protocol."""
    return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "grating",
    "movie_refresh_freq":10.0,
    "Screen": "%s",
    "shuffling":"full",
    "shuffling-seed":34,
    "-----------------------------------------------------------------1":0,
    "presentation-duration": 2.0,
    "presentation-interstim-period": 1.0,
    "N-repeat": %i,
    "-----------------------------------------------------------------2":0,
    "x-center-1": -15.0, "x-center-2": 105.0, "N-x-center": 7,
    "y-center-1": 0.0, "y-center-2": 60.0, "N-y-center": 4,
    "-----------------------------------------------------------------3":0,
    "spatial-freq": 0.06,
    "contrast":1.0,
    "speed":2,
    "angle":0,
    "radius": 12.5
  }
  """ % (Screen, Nrepeat)


if __name__ == '__main__':
    Nrepeat = 30
    build_movie(PM(Screen, Nrepeat), name='precise-mapping', rm=True)
