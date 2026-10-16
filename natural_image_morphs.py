"""
Shared tools for the natural-image morphing scripts
    - Natural-Images-Morphing.py            (Fourier phase morphing)
    - Natural-Images-Diffusion-Morphing.py  (Stable Diffusion latent morphing)

image loading, luminance/contrast/spectrum equalization, mouse-relevant
similarity metrics (mouse acuity, V1 energy model), calibration of `s` and figures
"""
import os, glob
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(ROOT, 'Natural-Images-Allen')
OUT_DIR = os.path.join(ROOT, 'Natural-Images-Morphs')

# --- display geometry (Allen Brain Observatory: 1920 px <-> ~120 deg, ignoring the spherical warping)
DEG_PER_PX = 120. / 1920.
MODEL_DOWNSAMPLE = 4          # V1 model / mouse-view metrics computed at 0.25 deg/px (Nyquist 2 cpd)
MOUSE_ACUITY = 0.5            # cycles/deg, gain=0.5 at this frequency

# --- stimulus statistics
MEAN_LUM = 0.5                # in [0,1] screen units
RMS_CONTRAST = 0.2            # in [0,1] screen units


# ------------------------------------------------------------------
#  images
# ------------------------------------------------------------------
def list_images(folder=IMG_DIR):
    files = glob.glob(os.path.join(folder, '*.jpeg'))
    return sorted(files, key=lambda f: int(os.path.basename(f).split('.')[0]))


def load_images(folder=IMG_DIR):
    files = list_images(folder)
    imgs = [np.asarray(Image.open(f).convert('L'), dtype=float) / 255. for f in files]
    h = min(im.shape[0] for im in imgs)
    w = min(im.shape[1] for im in imgs)
    return np.array([im[:h, :w] for im in imgs]), [os.path.basename(f) for f in files]


def normalize(x, mean_lum=MEAN_LUM, rms_contrast=RMS_CONTRAST):
    """ set mean luminance and RMS contrast, clip to the screen range """
    x = (x - x.mean()) / x.std()
    return np.clip(mean_lum + rms_contrast * x, 0, 1)


def wrap(phi):
    return (phi + np.pi) % (2 * np.pi) - np.pi


def periodic_smooth(u):
    """
    periodic + smooth decomposition (Moisan 2011, J Math Imaging Vis):
    u = p + s, with p periodic (no FFT boundary cross artifact) and s smooth
    """
    v = np.zeros_like(u)
    v[0, :] += u[-1, :] - u[0, :]
    v[-1, :] += u[0, :] - u[-1, :]
    v[:, 0] += u[:, -1] - u[:, 0]
    v[:, -1] += u[:, 0] - u[:, -1]
    q = np.arange(u.shape[0])[:, None]
    r = np.arange(u.shape[1])[None, :]
    den = 2 * np.cos(2 * np.pi * q / u.shape[0]) + 2 * np.cos(2 * np.pi * r / u.shape[1]) - 4
    den[0, 0] = 1.
    S = np.fft.fft2(v) / den
    S[0, 0] = 0.
    s = np.real(np.fft.ifft2(S))
    return u - s, s


def phase_spectrum(img):
    """ (amplitude, phase) of the periodic component of img, and its smooth component """
    p, s = periodic_smooth(img - img.mean())
    F = np.fft.fft2(p)
    return np.abs(F), np.angle(F), s


def phase_morph(specA, specB, w, amp=None, **kwargs):
    """
    Fourier phase morph between images A (w=0) and B (w=1) given by their `phase_spectrum`;
    amplitude spectrum: `amp` if given, else the mean of A and B
    """
    (ampA, phiA, sA), (ampB, phiB, sB) = specA, specB
    if amp is None:
        amp = 0.5 * (ampA + ampB)
    phi = phiA + w * wrap(phiB - phiA)
    x = np.real(np.fft.ifft2(amp * np.exp(1j * phi)))
    return normalize(x + (1 - w) * sA + w * sB, **kwargs)


def radial_bins(shape, n_bins=64):
    """ index of the radial spatial-frequency bin of each Fourier coefficient """
    fx, fy = freq_grid(shape, 1.)
    f = np.sqrt(fx**2 + fy**2)
    return np.minimum((f / f.max() * n_bins).astype(int), n_bins - 1)


def equalize_pair(x1, x2, mode='radial', **kwargs):
    """
    equalize the amplitude spectra of the two images of a pair, keeping their phases,
    then set the same mean luminance and RMS contrast
        mode='full'   : both get the mean 2D amplitude spectrum of the pair
        mode='radial' : both get the mean radially-averaged amplitude spectrum
                        (same energy at each spatial frequency, each image keeps
                        its own orientation content -> fewer artifacts)
        mode='none'   : only luminance & contrast
    """
    if mode == 'none':
        return normalize(x1, **kwargs), normalize(x2, **kwargs)
    (p1, s1), (p2, s2) = periodic_smooth(x1 - x1.mean()), periodic_smooth(x2 - x2.mean())
    F1, F2 = np.fft.fft2(p1), np.fft.fft2(p2)
    if mode == 'full':
        amp = 0.5 * (np.abs(F1) + np.abs(F2))
        F1, F2 = amp * np.exp(1j * np.angle(F1)), amp * np.exp(1j * np.angle(F2))
    elif mode == 'radial':
        bins = radial_bins(F1.shape)
        r1 = np.bincount(bins.ravel(), np.abs(F1).ravel()) / np.bincount(bins.ravel())
        r2 = np.bincount(bins.ravel(), np.abs(F2).ravel()) / np.bincount(bins.ravel())
        target = 0.5 * (r1 + r2)
        F1 = F1 * (target / (r1 + 1e-12))[bins]
        F2 = F2 * (target / (r2 + 1e-12))[bins]
    return tuple(normalize(np.real(np.fft.ifft2(F)) + s, **kwargs) for F, s in ((F1, s1), (F2, s2)))


# ------------------------------------------------------------------
#  mouse-relevant similarity metrics
# ------------------------------------------------------------------
def downsample(img, k):
    h, w = (img.shape[0] // k) * k, (img.shape[1] // k) * k
    return img[:h, :w].reshape(h // k, k, w // k, k).mean(axis=(1, 3))


def freq_grid(shape, deg_per_px):
    fy = np.fft.fftfreq(shape[0], deg_per_px)[:, None]
    fx = np.fft.fftfreq(shape[1], deg_per_px)[None, :]
    return fx, fy


def mouse_view(img, deg_per_px=DEG_PER_PX, acuity=MOUSE_ACUITY):
    """ Gaussian low-pass, gain = 0.5 at the acuity limit """
    fx, fy = freq_grid(img.shape, deg_per_px)
    sigma = acuity / np.sqrt(2 * np.log(2))
    G = np.exp(-(fx**2 + fy**2) / (2 * sigma**2))
    return np.real(np.fft.ifft2(np.fft.fft2(img) * G))


class V1EnergyModel:
    """
    Bank of complex cells (quadrature Gabor energy) tiling the visual field.
    SF range follows mouse V1 tuning (~0.02-0.3 cpd).
    """

    def __init__(self, shape, deg_per_px,
                 sfs=(0.04, 0.08, 0.16, 0.32), n_ori=8,
                 bandwidth=0.5, grid_deg=4.):
        fx, fy = freq_grid(shape, deg_per_px)
        filters = []
        for sf in sfs:
            for theta in np.arange(n_ori) * np.pi / n_ori:
                f0x, f0y = sf * np.cos(theta), sf * np.sin(theta)
                sig = bandwidth * sf
                # one-sided Gaussian in Fourier space -> complex (quadrature) Gabor output
                filters.append(np.exp(-((fx - f0x)**2 + (fy - f0y)**2) / (2 * sig**2)))
        self.filters = np.array(filters)
        step = max(1, int(round(grid_deg / deg_per_px)))
        self.sl = (slice(step // 2, None, step), slice(step // 2, None, step))
        self.mu, self.sd = 0., 1.

    def raw(self, img):
        F = np.fft.fft2(img - img.mean())
        resp = np.abs(np.fft.ifft2(F[None] * self.filters, axes=(-2, -1)))
        return resp[:, self.sl[0], self.sl[1]].ravel()

    def fit_normalization(self, imgs):
        R = np.array([self.raw(im) for im in imgs])
        self.mu, self.sd = R.mean(0), R.std(0) + 1e-12

    def __call__(self, img):
        return (self.raw(img) - self.mu) / self.sd


def build_v1_model(stimuli):
    """ V1 model working on downsampled stimuli, unit responses z-scored over `stimuli` """
    ds = [downsample(x, MODEL_DOWNSAMPLE) for x in stimuli]
    v1 = V1EnergyModel(ds[0].shape, DEG_PER_PX * MODEL_DOWNSAMPLE)
    v1.fit_normalization(ds)
    return v1


def corr(x, y):
    return float(np.corrcoef(x.ravel(), y.ravel())[0, 1])


METRICS = {'pixel': 'pixel correlation (full resolution)',
           'mouse': 'pixel correlation (mouse acuity)',
           'v1': 'V1 energy-model response correlation'}


def similarity_metrics(x1, x2, v1):
    d1, d2 = downsample(x1, MODEL_DOWNSAMPLE), downsample(x2, MODEL_DOWNSAMPLE)
    dpp = DEG_PER_PX * MODEL_DOWNSAMPLE
    return {'pixel': corr(x1, x2),
            'mouse': corr(mouse_view(d1, dpp), mouse_view(d2, dpp)),
            'v1': corr(v1(d1), v1(d2))}


# ------------------------------------------------------------------
#  calibration of `s`
# ------------------------------------------------------------------
def random_pairs(n_images, n_pairs, seed=1):
    rng = np.random.default_rng(seed)
    return [tuple(int(k) for k in rng.choice(n_images, 2, replace=False)) for _ in range(n_pairs)]


def calibrate(make_pair, pairs, s_grid, v1):
    """
    make_pair(i, j, s_raw) -> (x1, x2)
    returns the similarity metrics (pairs x s_grid) and the calibration function
    mapping a target similarity (normalized V1-model similarity) to the raw s
    """
    calib = {k: np.zeros((len(pairs), len(s_grid))) for k in METRICS}
    clipped = []
    for p, (i, j) in enumerate(pairs):
        for k, s in enumerate(s_grid):
            x1, x2 = make_pair(i, j, s)
            clipped.append(np.mean((x1 == 0) | (x1 == 1)))
            for key, val in similarity_metrics(x1, x2, v1).items():
                calib[key][p, k] = val
        print('calibration pair %i/%i' % (p + 1, len(pairs)), end='\r')
    print('\nclipped pixels: %.2f%% on average' % (100 * np.mean(clipped)))

    # normalized V1 similarity: 0 at s=0, 1 at s=1, forced monotonic
    v1_mean = calib['v1'].mean(0)
    v1_norm = np.maximum.accumulate((v1_mean - v1_mean[0]) / (v1_mean[-1] - v1_mean[0]))
    # strictly increasing (flat parts -> lowest s), still 0 at s=0 and 1 at s=1
    ramp = 1e-6 * np.arange(len(s_grid))
    v1_norm = (v1_norm + ramp) / (1 + ramp[-1])

    def calibrated_s(s_target):
        """ raw morph similarity giving a normalized V1-model similarity = s_target """
        return np.interp(s_target, v1_norm, s_grid)

    return calib, v1_norm, calibrated_s


def save_calibration(out_dir, s_grid, pairs, v1_norm, calib, **extra):
    np.savez(os.path.join(out_dir, 'calibration.npz'),
             s_grid=s_grid, pairs=np.array(pairs), v1_norm=v1_norm,
             deg_per_px=DEG_PER_PX, mouse_acuity=MOUSE_ACUITY,
             mean_lum=MEAN_LUM, rms_contrast=RMS_CONTRAST,
             **calib, **extra)


# ------------------------------------------------------------------
#  figures & export
# ------------------------------------------------------------------
SERIES = {'pixel': '#2a78d6', 'mouse': '#eb6834', 'v1': '#1baf7a'}
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})


def show(ax, img, title=None):
    ax.imshow(img, cmap='gray', vmin=0, vmax=1, interpolation='lanczos')
    ax.axis('off')
    if title:
        ax.set_title(title, fontsize=8)


def plot_continuum(morph, pairs, imgs, names, title, ws=np.linspace(0, 1, 7)):
    """ morph(i, j, w) -> image """
    fig, AX = plt.subplots(len(pairs), len(ws) + 2, figsize=(14, 1.45 * len(pairs) + .4))
    for r, (i, j) in enumerate(pairs):
        show(AX[r, 0], imgs[i], 'original %s' % names[i] if r == 0 else None)
        for c, w in enumerate(ws):
            show(AX[r, c + 1], morph(i, j, w), 'w = %.2f' % w if r == 0 else None)
        show(AX[r, -1], imgs[j], 'original %s' % names[j] if r == 0 else None)
    fig.suptitle(title)
    fig.tight_layout()
    return fig


def plot_pairs(make_pair, calibrated_s, i, j, s_levels, v1, title):
    fig, AX = plt.subplots(4, len(s_levels), figsize=(2.1 * len(s_levels), 6.6))
    for c, s in enumerate(s_levels):
        x1, x2 = make_pair(i, j, calibrated_s(s))
        m = similarity_metrics(x1, x2, v1)
        show(AX[0, c], x1, 's = %.2f  (raw %.2f)\nV1 r = %.2f' % (s, calibrated_s(s), m['v1']))
        show(AX[1, c], x2)
        show(AX[2, c], np.clip(mouse_view(x1), 0, 1))
        show(AX[3, c], np.clip(mouse_view(x2), 0, 1))
    for r, label in enumerate(['stim 1', 'stim 2', 'stim 1\nmouse view', 'stim 2\nmouse view']):
        AX[r, 0].text(-0.06, 0.5, label, transform=AX[r, 0].transAxes,
                      ha='right', va='center', fontsize=8)
    fig.suptitle(title)
    fig.tight_layout()
    return fig


def plot_calibration(calib, s_grid, calibrated_s, n_pairs):
    fig, AX = plt.subplots(1, 2, figsize=(9, 3.6))
    for key, label in METRICS.items():
        m, sd = calib[key].mean(0), calib[key].std(0)
        AX[0].fill_between(s_grid, m - sd, m + sd, color=SERIES[key], alpha=0.15, lw=0)
        AX[0].plot(s_grid, m, color=SERIES[key], lw=2, label=label)
    AX[0].plot([0, 1], [0, 1], color='0.7', lw=1, ls=':', zorder=0)
    AX[0].set_xlabel('raw morph similarity s')
    AX[0].set_ylabel('similarity of the two stimuli (r)')
    AX[0].set_title('Metrics vs. raw s  (mean ± s.d., %i pairs)' % n_pairs, fontsize=9)
    AX[0].legend(frameon=False, fontsize=8, loc='upper left')
    AX[0].grid(color='0.92', lw=0.6)

    s_fine = np.linspace(0, 1, 101)
    AX[1].plot(s_fine, calibrated_s(s_fine), color=SERIES['v1'], lw=2)
    AX[1].plot([0, 1], [0, 1], color='0.7', lw=1, ls=':', zorder=0)
    AX[1].set_xlabel('target similarity s (normalized V1-model similarity)')
    AX[1].set_ylabel('raw morph similarity to use')
    AX[1].set_title('Calibration map', fontsize=9)
    AX[1].grid(color='0.92', lw=0.6)
    fig.tight_layout()
    return fig


def export_stimuli(make_pair, calibrated_s, pairs, s_levels, v1, names, out_dir):
    """ 8-bit PNG stimulus pairs + an index csv """
    stim_dir = os.path.join(out_dir, 'stimuli')
    os.makedirs(stim_dir, exist_ok=True)
    rows = ['pair,image_1,image_2,s_target,s_raw,v1_r,mouse_r,stim_1,stim_2']
    for p, (i, j) in enumerate(pairs):
        for s in s_levels:
            x1, x2 = make_pair(i, j, calibrated_s(s))
            m = similarity_metrics(x1, x2, v1)
            fn = ['pair-%02i_s-%.2f_stim-%i.png' % (p, s, k) for k in (1, 2)]
            for x, f in zip((x1, x2), fn):
                Image.fromarray(np.round(255 * x).astype(np.uint8)).save(os.path.join(stim_dir, f))
            rows.append('%i,%s,%s,%.2f,%.4f,%.4f,%.4f,%s,%s' % (
                p, names[i], names[j], s, calibrated_s(s), m['v1'], m['mouse'], *fn))
    with open(os.path.join(out_dir, 'stimuli.csv'), 'w') as f:
        f.write('\n'.join(rows) + '\n')
    print('exported %i stimulus pairs to %s' % (len(rows) - 1, stim_dir))
