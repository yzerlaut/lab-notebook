#!/usr/bin/env python
"""
Vision-survey protocol of Sofia (from visualStim-protocols-BEFORE/Sofia):
    - vision-survey-short+1sPrePostOpto
            center patch, full-field drifting grating, grey screen, natural image, looming
            optogenetic stimulation on the odd repeats

    former variants (not built by default, see __main__):
    - vision-survey+1sPrePostOpto-old:     natural image instead of the drifting grating,
                                                no interstim jitter
    - vision-survey+1sPrePostOpto-old-old: same, without the "Opto-stim" settings

natural image: run prepare_images.py first
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_movie import build_movie, NI_FOLDER

Screen = "Dell-2020"

# visual degrees per image pixel: the 1280 pixels of the image span the screen width
#   (Dell-2020, "cm" units: 2*arctan(24cm/15cm) / 1280px)
DEG_PER_PIXEL_FULL_WIDTH = 0.0906

# common settings of the sub-protocols
SUB = {"Presentation": "Stimuli-Sequence",
       "Screen": Screen,
       "units": "cm",
       "movie_refresh_freq": 30.0,
       "presentation-prestim-period": 6,
       "presentation-poststim-period": 6,
       "presentation-interstim-period": 4,
       "presentation-blank-screen-color": 0.5}


def center_patch():
    return {**SUB, "Stimulus": "grating",
            "presentation-duration": 1,
            "speed": 0, "phase": 0, "spatial-freq": 0.04,
            "x-center": 0.0, "y-center": 0.0, "angle": 0.0,
            "radius-1": 20, "radius-2": 50, "N-radius": 2,
            "contrast-1": 0.2, "contrast-2": 1.0, "N-contrast": 3,
            "N-repeat": 20}


def ff_drifting_grating():
    return {**SUB, "Stimulus": "grating",
            "presentation-duration": 2,
            "speed": 2, "phase": 0, "spatial-freq": 0.04,
            "x-center": 0.0, "y-center": 0.0, "radius": 200.0, "angle": 0.0,
            "contrast-1": 0.2, "contrast-2": 1.0, "N-contrast": 3,
            "N-repeat": 20}


def grey_screen():
    return {**SUB, "Stimulus": "uniform_bg",
            "presentation-duration": 2,
            "screen-color": 0.5,
            "N-repeat": 20}


def natural_image():
    # former Image-ID 1 of the physion NI_bank: 2.jpg (= 2.png of the NI_bank of Sofia)
    return {**SUB, "Stimulus": "images",
            "presentation-duration": 2.0,
            "NI_FOLDER": NI_FOLDER,
            "Image-ID-1": "2.png",
            "degree-per-pixel-of-image": DEG_PER_PIXEL_FULL_WIDTH,
            "radius": 200,
            "contrast-1": 0.2, "contrast-2": 1.0, "N-contrast": 3,
            "N-repeat": 20}


def looming():
    return {**SUB, "Stimulus": "looming_stim",
            "presentation-duration": 5.0,
            "looming-duration": 1.0, "end-duration": 4.0,
            "looming-nonlinearity": 3,
            "radius-start": 0.5, "radius-end": 120,
            "x-center": 0.0, "y-center": 0.0,
            "N-repeat": 10}


def VisionSurvey(version='short', Screen=Screen):
    """
    returns the multiprotocol json and the {filename: json} of its sub-protocols
        version: 'short', 'old' or 'old-old'
    """
    survey = {
        "Presentation": "multiprotocol",
        "shuffling": "full-with-alternate-even-odd-repeats",
        "shuffling-seed": 34,
        "movie_refresh_freq": 30.0,
        "units": "cm",
        "Screen": Screen,
        "presentation-prestim-period": 10.0,
        "presentation-poststim-period": 10.0,
        "presentation-interstim-period": 6.0,
        "presentation-blank-screen-color": 0.5}

    if version=='short':
        survey["presentation-interstim-jitter"] = 2.0
        protocol2 = ('protocol-ff_drifting_grating.json', ff_drifting_grating())
    else:
        protocol2 = ('protocol-natural-images.json', natural_image())
        if version=='old':
            survey["presentation-interstim-jitter"] = 0.0

    if version!='old-old':
        survey["Opto-stim"] = {"pre_window": 1.0, "post_window": 1.0,
                               **{"Protocol-%i" % i: {"trials": "odd"} for i in range(1, 6)}}

    subprotocols = [('protocol-center-patch.json', center_patch()),
                    protocol2,
                    ('protocol-grey-screen.json', grey_screen()),
                    ('protocol-natural-images.json', natural_image()),
                    ('protocol-looming.json', looming())]
    for i, (filename, protocol) in enumerate(subprotocols, start=1):
        survey['Protocol-%i' % i] = filename

    return json.dumps(survey, indent=4),\
        {filename: json.dumps(protocol, indent=4) for filename, protocol in subprotocols}


if __name__ == '__main__':

    protocol, subprotocols = VisionSurvey('short')
    build_movie(protocol, name='vision-survey-short+1sPrePostOpto',
                subprotocols=subprotocols)

    # protocol, subprotocols = VisionSurvey('old')
    # build_movie(protocol, name='vision-survey+1sPrePostOpto-old',
    #             subprotocols=subprotocols)

    # protocol, subprotocols = VisionSurvey('old-old')
    # build_movie(protocol, name='vision-survey+1sPrePostOpto-old-old',
    #             subprotocols=subprotocols)
