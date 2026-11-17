#!/usr/bin/env python
"""
Natural-images protocol of Cibele (from visualStim-protocols-BEFORE/Cibele):
    - 10NaturalImages-2contrasts-10repeats

    (same protocol as Sofia's: identical protocol.json and visual-stim.npy)

images stretched over the full screen, as with the former "natural_image" stimulus:
    1280x720 copies of the images (made by prepare_images.py, run here if missing)
    "lin-deg" units: constant angle per screen pixel -> 1 image pixel per screen pixel

the "Image-ID" values are those of the former protocol
    (former Image-ID k: k-th file of the sorted listing of the image folder, from 0)
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_movie import build_movie, NI_FOLDER
from prepare_images import prepare_images

Screen = "Dell-2020"

# visual degrees per screen pixel of the Dell-2020 in "lin-deg" units
#       = arctan(48cm/1280px/15cm)
DEG_PER_PIXEL_LIN_DEG = 0.1432

# former Image-ID 1..10: files 1..10 of the sorted listing
#       ["1.png", "10.png", "11.png", "2.png", ..., "9.png"]
TEN_IMAGES = ['10.png', '11.png', '2.png', '3.png', '4.png',
              '5.png', '6.png', '7.png', '8.png', '9.png']


def images(filenames):
    """ "Image-ID-k": filename """
    return {'Image-ID-%i' % (k+1): f for k, f in enumerate(filenames)}


def NaturalImages(filenames, contrasts, Nrepeat,
                  interstim=4, shuffling=None,
                  Screen=Screen):
    protocol = {
        "Presentation": "Stimuli-Sequence",
        "Stimulus": "images",
        "Screen": Screen,
        "units": "lin-deg",
        "movie_refresh_freq": 30.0,
        "presentation-duration": 2,
        "presentation-prestim-period": 4,
        "presentation-poststim-period": 4,
        "presentation-interstim-period": interstim,
        "presentation-blank-screen-color": 0.5,
        "N-repeat": Nrepeat,
        "NI_FOLDER": NI_FOLDER,
        "degree-per-pixel-of-image": DEG_PER_PIXEL_LIN_DEG,
        "radius": 200,
        "contrast-1": contrasts[0], "contrast-2": contrasts[1], "N-contrast": contrasts[2],
        **images(filenames)}
    if shuffling is not None:
        protocol.update({"shuffling": shuffling, "shuffling-seed": 1})
    return json.dumps(protocol, indent=4)


if __name__ == '__main__':

    if not all(os.path.isfile(os.path.join(NI_FOLDER, f)) for f in TEN_IMAGES):
        prepare_images()

    build_movie(NaturalImages(TEN_IMAGES, (0.5, 1.0, 2), 10,
                              interstim=5, shuffling='full'),
                name='10NaturalImages-2contrasts-10repeats')
