# %% [markdown]
# # Natural-image morphing with a controlled similarity parameter `s`
#
# Goal: build pairs of stimuli derived from real natural images whose similarity
# is set by `s`:  s=0 -> two unrelated natural images,  s=1 -> the same image.
#
# Method: Fourier *phase* morphing with a *fixed* amplitude spectrum.
#   - the two stimuli of a pair share the same amplitude spectrum (mean of A and B,
#     or optionally the mean over the whole set), and all stimuli share the same mean
#     luminance and RMS contrast,
#   - FFT boundary artifacts are avoided with the periodic + smooth decomposition
#     (Moisan 2011): the phase of the periodic part is morphed, the smooth part is blended,
#   - only the phase (i.e. the image structure) is interpolated between images A and B,
#   - so a decoder cannot rely on low-level statistics.
#
# The raw morph weight is not linear in "what a mouse V1 sees", so we calibrate it
# with (1) a low-pass filter at mouse acuity and (2) a simple V1 energy model,
# and we re-map `s` so that the model V1 similarity grows linearly with `s`.
#
# Methods: physion/visual_stim/natural_images (morphing, mouse_vision, calibration, plots),
# settings (paths, geometry, stimulus statistics): settings.py.
# See Diffusion-Morphing.py for the Stable Diffusion alternative.

# %%
import os
import numpy as np
import matplotlib.pyplot as plt

import settings
from physion.visual_stim.natural_images import images, morphing, mouse_vision, calibration, plots

OUT_DIR = os.path.join(settings.OUT_DIR, 'phase')

AMPLITUDE = 'pair-mean'       # fixed amplitude spectrum:
#   'pair-mean' : mean of the two images of a pair  -> identical spectra within a pair (default)
#   'set-mean'  : mean over the whole image set     -> identical spectra across all stimuli

# --- calibration
N_CALIB_PAIRS = 30
S_GRID = np.linspace(0, 1, 21)
SEED = 1

# --- export
N_EXPORT_PAIRS = 5
S_EXPORT = [0., 0.25, 0.5, 0.75, 0.9, 1.]    # calibrated similarity levels

# %% [markdown]
# ## Load images, build morpher and V1 model

# %%
imgs, names = images.load_images(settings.IMG_DIR)
morpher = morphing.PhaseMorpher(imgs, amplitude=AMPLITUDE, **settings.NORM)
deg_per_px = settings.deg_per_px(imgs[0].shape)
print('%i images, %ix%i px (%.0fx%.0f deg, %.4f deg/px)' % (
    len(imgs), *imgs[0].shape, *(np.array(imgs[0].shape) * deg_per_px), deg_per_px))

v1 = mouse_vision.build_v1_model([morpher.equalized(i) for i in range(len(imgs))],
                                 deg_per_px=deg_per_px)
print('V1 model: %i units' % v1.mu.size)

# %% [markdown]
# ## Calibration: similarity metrics as a function of raw `s`

# %%
calib_pairs = calibration.random_pairs(len(imgs), N_CALIB_PAIRS, seed=SEED)
calib, v1_norm, calibrated_s = calibration.calibrate(morpher.pair, calib_pairs, S_GRID, v1)

os.makedirs(os.path.join(OUT_DIR, 'figures'), exist_ok=True)
calibration.save_calibration(OUT_DIR, S_GRID, calib_pairs, v1_norm, calib, v1=v1,
                             amplitude=AMPLITUDE, **settings.NORM)
for s in S_EXPORT:
    print('target similarity %.2f  ->  raw s = %.3f' % (s, calibrated_s(s)))

# %% [markdown]
# ## Figures

# %%
fig = plots.plot_continuum(morpher.morph, calib_pairs[:3], imgs, names,
                           'Phase morphing continuum (amplitude spectrum: %s, fixed luminance & RMS contrast)' % AMPLITUDE)
plots.save(fig, os.path.join(OUT_DIR, 'figures', '1_morph-continuum.png'))

i, j = calib_pairs[0]
fig = plots.plot_pairs(morpher.pair, calibrated_s, i, j, S_EXPORT, v1,
                       'Phase morphing: stimulus pairs vs. calibrated similarity  (%s / %s)' % (names[i], names[j]))
plots.save(fig, os.path.join(OUT_DIR, 'figures', '2_pairs-vs-similarity.png'))

fig = plots.plot_calibration(calib, S_GRID, calibrated_s, N_CALIB_PAIRS)
plots.save(fig, os.path.join(OUT_DIR, 'figures', '3_calibration.png'))

# %% [markdown]
# ## Export stimulus pairs (8-bit PNG, original resolution)

# %%
calibration.export_stimuli(morpher.pair, calibrated_s, calib_pairs[:N_EXPORT_PAIRS],
                           S_EXPORT, v1, names, OUT_DIR)

# %%
plt.show()
