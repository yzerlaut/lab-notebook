#!/usr/bin/env python
"""
5-minute uniform screens for Sally: "5min-black-screen" (lum.=0) and
"5min-grey-screen" (lum.=0.5).

A single "uniform_bg" episode of 5min, with no blank before or after
(prestim = interstim = poststim = 0, blank color = screen color).

run from the root of the repository (as the other scripts of this folder):
    uv run python build-visualStim-protocols-Sally/uniform_screens.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_movie import build_movie

# Screen="Dell-2020-low-resolution"
# Screen="LN-VR-3screens"
Screen = "LN-2screens"

DURATION = 5*60.  # s

SCREENS = {'5min-black-screen': 0.,
           '5min-grey-screen': 0.5}


def US(Screen, luminance, duration=DURATION):
    """ Uniform Screen: one episode of uniform background at "luminance" """
    return """{
    "Presentation": "Single-Stimulus",
    "Stimulus": "uniform_bg",
    "movie_refresh_freq": 10.0,
    "Screen": "%s",
    "-----------------------------------------------------------------1":0,
    "presentation-duration": %.1f,
    "presentation-prestim-period": 0.0,
    "presentation-interstim-period": 0.0,
    "presentation-poststim-period": 0.0,
    "presentation-blank-screen-color": %.2f,
    "-----------------------------------------------------------------2":0,
    "screen-color": %.2f
  }
  """ % (Screen, duration, luminance, luminance)


if __name__ == '__main__':
    for name, luminance in SCREENS.items():
        build_movie(US(Screen, luminance), name=name)
