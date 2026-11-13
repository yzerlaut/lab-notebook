#!/usr/bin/env python
"""
Natural images of Sofia's protocols, as displayed by the former "natural_image" stimulus:
    stretched over the full Dell-2020 screen (1280x720 pixels)

the "images" stimulus of physion needs images of the same size,
    -> 1280x720 copies in NI_FOLDER (see build_movie.py), keeping the filenames

    - NI_bank of the former protocols (visualStim-protocols-BEFORE/Sofia/NI_bank)
    - "3.jpg" of the physion NI_bank (2nd image of "2NaturalImages-8contrasts-15repeats"),
        saved as "physion-3.png"
"""

import os
import sys
import glob

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_movie import NI_FOLDER, PHYSION_SRC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = {os.path.basename(f): f for f in glob.glob(
    os.path.join(ROOT, 'visualStim-protocols-BEFORE', 'Sofia', 'NI_bank', '*.png'))}
SOURCES['physion-3.png'] = os.path.join(PHYSION_SRC, 'physion', 'visual_stim', 'NI_bank', '3.jpg')

RESOLUTION = (1280, 720) # Dell-2020 screen


def prepare_images():
    os.makedirs(NI_FOLDER, exist_ok=True)
    for name, source in sorted(SOURCES.items()):
        img = Image.open(source).convert('RGB').resize(RESOLUTION, Image.BILINEAR)
        img.save(os.path.join(NI_FOLDER, name))
        print(' - %s -> %s' % (source, os.path.join(NI_FOLDER, name)))


if __name__ == '__main__':
    prepare_images()
