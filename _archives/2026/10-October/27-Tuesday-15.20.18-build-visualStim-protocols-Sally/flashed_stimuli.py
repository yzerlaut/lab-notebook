#!/usr/bin/env python
"""Flashed Stimuli protocol for Sally."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_movie import build_movie

# Screen="Dell-2020-low-resolution"
# Screen="LN-VR-3screens"
Screen = "LN-2screens"


def FS(Screen, Nrepeat):
    """Flashed Stimuli protocol."""
    return """{
    "Presentation": "Stimuli-Sequence",
    "Stimulus": "uniform_bg",
    "movie_refresh_freq":10.0,
    "Screen": "%s",
    "-----------------------------------------------------------------1":0,
    "presentation-duration": 1.0,
    "presentation-interstim-period": 5.0,
    "presentation-blank-screen-color": 0.25,
    "N-repeat": %i,
    "-----------------------------------------------------------------3":0,
    "screen-color": 1.0
  }
  """ % (Screen, Nrepeat)


if __name__ == '__main__':
    Nrepeat = 100
    build_movie(FS(Screen, Nrepeat), name='flashed-stimuli')
