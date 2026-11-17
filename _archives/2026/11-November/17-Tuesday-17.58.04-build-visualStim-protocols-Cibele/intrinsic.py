#!/usr/bin/env python
"""
Intrinsic-imaging protocols of Cibele (from visualStim-protocols-BEFORE/Cibele/intrinsic):
    - intrinsic/flickering-bars-period6s/{up,down,left,right}.mkv
    - intrinsic/flickering-bars-period12s/{up,down,left,right}.mkv

one movie per bar direction (single episode), json of physion.intrinsic.build_protocols
"""

import os
import sys
import shutil
import subprocess
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_movie import OUTPUT_FOLDER, PHYSION_SRC

sys.path.insert(0, PHYSION_SRC)
from physion.intrinsic.build_protocols import build_json

Screen = "Dell-2020"
BG_COLOR = 0.2 # physion default


def build_bar_movie(json_string, target):
    """ builds the movie on the local disk and moves it to "target" """
    with tempfile.TemporaryDirectory() as build_folder:
        with open(os.path.join(build_folder, 'temp.json'), 'w') as f:
            f.write(json_string)
        subprocess.run([sys.executable, '-m', 'physion.visual_stim.build',
                        os.path.join(build_folder, 'temp.json'),
                        '-o', build_folder],
                       cwd=PHYSION_SRC, check=True)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.move(os.path.join(build_folder, 'temp', 'movie.mkv'), target)
        print(' --> moved to: "%s"' % target)


if __name__ == '__main__':

    for period in [6, 12]:
        for direction in ['up', 'down', 'left', 'right']:
            build_bar_movie(build_json(direction, screen=Screen,
                                       period=period, bg_color=BG_COLOR),
                            os.path.join(OUTPUT_FOLDER, 'intrinsic',
                                         'flickering-bars-period%is' % period,
                                         '%s.mkv' % direction))
