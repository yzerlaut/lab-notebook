"""
shared settings of the natural-image morphing notebooks: paths, display geometry, stimulus statistics

the methods are those of physion: physion/visual_stim/natural_images
(this module also puts physion/src on the python path)
"""
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, os.pardir, 'physion', 'src'))

# --- paths
# the 118 natural images of the Allen Brain Observatory
# IMG_DIR = os.path.join(os.path.expanduser('~'), 'Library', 'CloudStorage', 'OneDrive-ICM',
#                        'Lab-Notebook', 'visualStim-protocols', 'Natural-Images-Allen')
IMG_DIR = os.path.join(ROOT, 'Natural-Images-Allen')
OUT_DIR = os.path.join(ROOT, 'morphs')                  # phase/ and diffusion/ morph outputs
NATURALNESS_DIR = os.path.join(ROOT, 'naturalness')     # outputs of Naturalness.py

# --- display geometry (visual degrees per image pixel)
#   legacy: Allen Brain Observatory, 1920 px <-> ~120 deg (ignoring the spherical warping);
#   all the outputs in morphs/ and naturalness/ were computed with it
#   None: from the physion screen and protocol units below (visual_stim.geometry.deg_per_pixel)
DEG_PER_PX = 120. / 1920.
SCREEN, UNITS = 'Dell-2020', 'cm'

# --- stimulus statistics (kwargs of physion's images.normalize, in [0,1] screen units)
NORM = dict(mean_lum=0.5, rms_contrast=0.2)


def deg_per_px(image_shape):
    """ visual degrees per image pixel: DEG_PER_PX, or from SCREEN / UNITS if None """
    from physion.visual_stim.natural_images import mouse_vision
    return mouse_vision.resolve_deg_per_px(image_shape, SCREEN, UNITS, DEG_PER_PX)
