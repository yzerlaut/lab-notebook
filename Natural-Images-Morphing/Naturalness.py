"""
Naturalness of phase-morphed images: sparseness of filter responses

For every pair of images in Natural-Images-Allen (118 images -> 6903 pairs):
  - build the phase-morphing continuum (same morph as Phase-Morphing.py),
  - measure the sparseness of linear Gabor-filter responses (kurtosis) of each image,
    with the mouse V1 filter bank of the calibration (0.04-0.32 cpd, 8 orientations),
  - turn it into a naturalness index:
        1 = as sparse as the original images, 0 = as Gaussian as a phase-scrambled image
    (natural images have heavy-tailed filter responses; phase randomization makes them Gaussian),
  - rank the pairs by the naturalness of their least natural intermediate image,
  - draw the continuum figure of each pair, file names prefixed by the rank.

This is physion's pipeline (physion/visual_stim/natural_images/run_naturalness.py)
with the defaults of settings.py (images, output folder, geometry, stimulus statistics).

Usage (from this folder):
    python Naturalness.py                   # all pairs, all figures
    python Naturalness.py --max-pairs 20    # quick test on 20 random pairs
    python Naturalness.py --workers 8 --n-figures 500
    python Naturalness.py --help            # all options

Cost: ~1 s per pair and ~1.5 s per figure on one core (all pairs: ~15 + 20 min on 8 cores),
~1 GB of figures for all pairs.

Outputs (in naturalness/):
    pairs_sorted.csv   one row per pair, best pairs first
    sparseness.npz     all kurtosis values (per pair, morph weight, spatial frequency)
    summary.png        naturalness vs. morph weight over all pairs + score histogram
    top-pairs.png / bottom-pairs.png   midpoint images of the best / worst pairs
    continuum/rank-00001_56-61.png ...  continuum figure of each pair
"""
import settings
from physion.visual_stim.natural_images import run_naturalness


def parser():
    p = run_naturalness.parser()
    p.set_defaults(img_dir=settings.IMG_DIR, out_dir=settings.NATURALNESS_DIR,
                   deg_per_px=settings.DEG_PER_PX, screen=settings.SCREEN, units=settings.UNITS,
                   **settings.NORM)
    return p


if __name__ == '__main__':
    run_naturalness.main(parser().parse_args())
