#!/usr/bin/env python
"""Neurometric task protocol for Sally: decoding ambiguous natural images.

Phase morphs of pairs of Allen natural images (see Natural-Images-Morphing and the lab notes
Neurometric-Task-Design, Natural-Images-Morphing/Selection), at uniformly spaced morph weights w.

| stimulus                     | pairs | image pairs                | w | repeats |
| Radius=70 degree, Contrast=0.3 | 4     | 11-52, 3-11, 94-101, 17-26 | 5 | 10      |
| Radius=70 degree, Contrast=1.0 | 4     | 22-72, 13-95, 12-109, 9-11 | 5 | 10      |
| Radius=15 degree, Contrast=1.0 | 4     | 46-108, 4-23, 10-34, 7-49  | 5 | 10      |

Duration 1s, Interstim = 2s with Jitter = 1s
"""

import sys
import os
import csv
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# morphing settings (puts physion on the path)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'Natural-Images-Morphing'))

import numpy as np

from build_movie import build_movie, OUTPUT_FOLDER, NI_FOLDER
import settings
from physion.visual_stim.natural_images import images, spectrum, morphing

# Screen="Dell-2020-low-resolution"
# Screen="LN-VR-3screens"
Screen = "LN-2screens"

# visual angle of one image pixel (Allen images: 1174x918 pixels)
#   0.134 deg: as when the images are stretched over the Dell-2020 screen
#   (the geometry of the pair selection)
Degree_per_Pixel_of_Image = 0.134

# morph images (phase morphs, mean luminance 0.5, RMS contrast 0.2)
IMAGES_FOLDER = os.path.join(OUTPUT_FOLDER, 'images')

# morph weights: uniform
N_W = 5
W = np.linspace(0, 1, N_W)

# stimulus radius (degrees)
RADIUS_LARGE = 70.
RADIUS_SMALL = 15.

# (radius in degrees, contrast, image pairs)
STIMULI = [
    (RADIUS_LARGE, 0.3, ['11-52',  '3-11',  '94-101', '17-26']),
    (RADIUS_LARGE, 1.0, ['22-72',  '13-95', '12-109', '9-11']),
    (RADIUS_SMALL, 1.0, ['46-108', '4-23',  '10-34',  '7-49']),
]

Presentation_Duration = 1.0
Interstim = 2.0
Jitter = 1.0

x = 45.
y = 20.


def image_name(pair, w):
    return '%s_w=%.3f.png' % (pair, w)


def generate_images(folder=IMAGES_FOLDER):
    """
    phase morphs of all pairs at the weights W, added to `folder` (shared between protocols:
        the images already there are kept), with images.csv: file, pair, image A, image B, w
    """
    os.makedirs(folder, exist_ok=True)
    rows = {}
    if os.path.isfile(os.path.join(folder, 'images.csv')):
        with open(os.path.join(folder, 'images.csv'), newline='') as f:
            rows = {row['file']: row for row in csv.DictReader(f)}
    files = images.list_images(NI_FOLDER)
    shape = images.common_shape(files)
    for _, _, pairs in STIMULI:
        for pair in pairs:
            A, B = pair.split('-')
            missing = [w for w in W if not os.path.isfile(os.path.join(folder, image_name(pair, w)))]
            if missing:
                sA, sB = [spectrum.phase_spectrum(images.load_image(
                    os.path.join(NI_FOLDER, '%s.jpeg' % k), shape)) for k in (A, B)]
            for w in missing:
                images.save_image(morphing.phase_morph(sA, sB, w, **settings.NORM),
                                  os.path.join(folder, image_name(pair, w)))
            for w in W:
                rows[image_name(pair, w)] = dict(file=image_name(pair, w), pair=pair,
                                                 image_A='%s.jpeg' % A, image_B='%s.jpeg' % B, w=round(w, 4))
    with open(os.path.join(folder, 'images.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'pair', 'image_A', 'image_B', 'w'])
        writer.writeheader()
        writer.writerows(rows.values())
    print('%i images in %s' % (len(rows), folder))


def NT(Screen, Nrepeat, x, y):
    """
    Neurometric task protocol.
        returns the multiprotocol json and the {filename: json} of its sub-protocols
    """

    neurometricTask = """{
    "Presentation": "multiprotocol",
    "shuffling":"full",
    "shuffling-seed":34,
    "movie_refresh_freq":10.0,
    "units":"cm",
    "presentation-prestim-period": 15.0,
    "presentation-poststim-period": 5.0,
    "presentation-interstim-period": %.1f,
    "presentation-interstim-jitter": %.1f,
    "presentation-blank-screen-color": 0.5,
    "Screen": "%s",
  """ % (Interstim, Jitter, Screen)

    def single_protocol(radius, contrast, pair, w):
        protocol = """{
    "Presentation": "Stimulus-Sequence",
    "Stimulus": "images",
    "presentation-duration": %.1f,
    "presentation-interstim-period": %.1f,
    "N-repeat": %i,
    "_______________________________________________________________________1":0,
    "contrast": %.2f,
    "radius": %.2f,
    "x-center": %.2f,
    "y-center": %.2f,
    "NI_FOLDER": "%s",
    "degree-per-pixel-of-image": %.3f,
    "_______________________________________________________________________2":0,
    "Image-ID-1": "%s",
    "Screen": "%s"
  }""" % (Presentation_Duration, Interstim, Nrepeat, contrast, radius, x, y,
         IMAGES_FOLDER, Degree_per_Pixel_of_Image, image_name(pair, w), Screen)
        return protocol

    # one sub-protocol per image, named after it ("11-52_w=0.250.json"):
    #   the protocol name of the episodes gives the pair and w
    subprotocols = {}
    i = 1  # protocol counter
    for radius, contrast, pairs in STIMULI:
        for pair in pairs:
            for w in W:
                name = image_name(pair, w).replace('.png', '.json')
                subprotocols[name] = single_protocol(radius, contrast, pair, w)
                neurometricTask += '  "Protocol-%i": "%s",\n' % (i, name)
                i += 1

    neurometricTask = neurometricTask[:-2] + '}'

    return neurometricTask, subprotocols


if __name__ == '__main__':
    tic = time.time()
    generate_images()
    x, y = 45, 20
    Nrepeat = 10
    protocol, subprotocols = NT(Screen, Nrepeat, x, y)
    build_movie(protocol, name='task-imageID-x=%.0f-z=%.0f' % (x, y),
                subprotocols=subprotocols)
    print(' --> protocol generation took %.1f minutes ' % ((time.time() - tic) / 60.))
