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
# See Natural-Images-Diffusion-Morphing.py for the Stable Diffusion alternative,
# and natural_image_morphs.py for the shared tools (metrics, calibration, figures).

# %%
import os
import numpy as np
import matplotlib.pyplot as plt
import natural_image_morphs as nim

OUT_DIR = os.path.join(nim.OUT_DIR, 'phase')

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
# ## Phase morphing

# %%
class Morpher:
    """
    Phase morphing between natural images with a fixed amplitude spectrum
    (mean over the pair, or over the whole image set, see AMPLITUDE).
    """

    def __init__(self, imgs, amplitude=AMPLITUDE):
        self.imgs = imgs
        self.shape = imgs[0].shape
        self.amplitude = amplitude
        self._spectra = {}
        if amplitude == 'set-mean':
            self.set_amp = np.zeros(self.shape)
            for i in range(len(imgs)):
                self.set_amp += self.spectrum(i)[0] / len(imgs)

    def spectrum(self, i):
        """ (amplitude, phase) of the periodic component of image i, and its smooth component """
        if i not in self._spectra:
            if len(self._spectra) > 8:
                self._spectra.pop(next(iter(self._spectra)))
            self._spectra[i] = nim.phase_spectrum(self.imgs[i])
        return self._spectra[i]

    def morph(self, i, j, w):
        """ w=0 -> (spectrum-equalized) image i,  w=1 -> image j """
        amp = self.set_amp if self.amplitude == 'set-mean' else None
        return nim.phase_morph(self.spectrum(i), self.spectrum(j), w, amp=amp)

    def equalized(self, i):
        return self.morph(i, i, 0.)

    def pair(self, i, j, s_raw, anchored=False):
        """
        two stimuli with raw similarity s_raw (phase distance = 1-s_raw)
            symmetric (default): both stimuli move toward the A/B midpoint
            anchored: stimulus 1 is always image i, stimulus 2 moves from j to i
        """
        if anchored:
            return self.morph(i, j, 0.), self.morph(i, j, 1. - s_raw)
        d = (1. - s_raw) / 2.
        return self.morph(i, j, 0.5 - d), self.morph(i, j, 0.5 + d)


# %% [markdown]
# ## Load images, build morpher and V1 model

# %%
imgs, names = nim.load_images()
morpher = Morpher(imgs)
print('%i images, %ix%i px (%.0fx%.0f deg)' % (
    len(imgs), *imgs[0].shape, *(np.array(imgs[0].shape) * nim.DEG_PER_PX)))

v1 = nim.build_v1_model([morpher.equalized(i) for i in range(len(imgs))])
print('V1 model: %i units' % v1.mu.size)

# %% [markdown]
# ## Calibration: similarity metrics as a function of raw `s`

# %%
calib_pairs = nim.random_pairs(len(imgs), N_CALIB_PAIRS, seed=SEED)
calib, v1_norm, calibrated_s = nim.calibrate(morpher.pair, calib_pairs, S_GRID, v1)

os.makedirs(os.path.join(OUT_DIR, 'figures'), exist_ok=True)
nim.save_calibration(OUT_DIR, S_GRID, calib_pairs, v1_norm, calib)
for s in S_EXPORT:
    print('target similarity %.2f  ->  raw s = %.3f' % (s, calibrated_s(s)))

# %% [markdown]
# ## Figures

# %%
fig = nim.plot_continuum(morpher.morph, calib_pairs[:3], imgs, names,
                         'Phase morphing continuum (amplitude spectrum: %s, fixed luminance & RMS contrast)' % AMPLITUDE)
fig.savefig(os.path.join(OUT_DIR, 'figures', '1_morph-continuum.png'), dpi=150)

i, j = calib_pairs[0]
fig = nim.plot_pairs(morpher.pair, calibrated_s, i, j, S_EXPORT, v1,
                     'Phase morphing: stimulus pairs vs. calibrated similarity  (%s / %s)' % (names[i], names[j]))
fig.savefig(os.path.join(OUT_DIR, 'figures', '2_pairs-vs-similarity.png'), dpi=150)

fig = nim.plot_calibration(calib, S_GRID, calibrated_s, N_CALIB_PAIRS)
fig.savefig(os.path.join(OUT_DIR, 'figures', '3_calibration.png'), dpi=150)

# %% [markdown]
# ## Export stimulus pairs (8-bit PNG, original resolution)

# %%
nim.export_stimuli(morpher.pair, calibrated_s, calib_pairs[:N_EXPORT_PAIRS],
                   S_EXPORT, v1, names, OUT_DIR)

# %%
plt.show()
