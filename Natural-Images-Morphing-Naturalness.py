# %% [markdown]
# # Naturalness of phase-morphed images: sparseness of filter responses
#
# For every pair of images in Natural-Images-Allen (118 images -> 6903 pairs):
#   - build the phase-morphing continuum (same morph as Natural-Images-Morphing.py),
#   - measure the sparseness of linear Gabor-filter responses (kurtosis) of each image,
#     with the mouse V1 filter bank of the calibration (0.04-0.32 cpd, 8 orientations),
#   - turn it into a naturalness index:
#         1 = as sparse as the original images, 0 = as Gaussian as a phase-scrambled image
#     (natural images have heavy-tailed filter responses; phase randomization makes them Gaussian),
#   - rank the pairs by the naturalness of their least natural intermediate image,
#   - draw the continuum figure of each pair, file names prefixed by the rank.
#
# Usage (from the repository root):
#     python Natural-Images-Morphing-Naturalness.py                   # all pairs, all figures
#     python Natural-Images-Morphing-Naturalness.py --max-pairs 20    # quick test on 20 random pairs
#     python Natural-Images-Morphing-Naturalness.py --workers 8 --n-figures 500
#
# Cost: ~1 s per pair and ~1.5 s per figure on one core (all pairs: ~15 + 20 min on 8 cores),
# ~1 GB of figures for all pairs.
#
# Outputs (in Natural-Images-Morphs/phase/naturalness/):
#     pairs_sorted.csv   one row per pair, best pairs first
#     sparseness.npz     all kurtosis values (per pair, morph weight, spatial frequency)
#     summary.png        naturalness vs. morph weight over all pairs + score histogram
#     top-pairs.png / bottom-pairs.png   midpoint images of the best / worst pairs
#     continuum/rank-00001_56-61.png ...  continuum figure of each pair

# %%
import os, time, argparse, itertools
from multiprocessing import Pool
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import natural_image_morphs as nim

N_W = 7                       # number of morph weights in the continuum (incl. both ends)
SFS = (0.04, 0.08, 0.16, 0.32)
N_ORI = 8
MIN_CONTRAST = 0.5            # min kurtosis difference natural - scrambled (avoids dividing by ~0)

# %% [markdown]
# ## Sparseness of filter responses

# %%
_W = {}   # per-worker state


def init_worker(img_dir, shape, ws):
    _W['img_dir'], _W['shape'], _W['ws'] = img_dir, shape, ws
    ds_shape = nim.downsample(np.zeros(shape), nim.MODEL_DOWNSAMPLE).shape
    _W['filters'] = nim.V1EnergyModel(ds_shape, nim.DEG_PER_PX * nim.MODEL_DOWNSAMPLE,
                                      sfs=SFS, n_ori=N_ORI).filters


def load_image(fn):
    img = np.asarray(Image.open(os.path.join(_W['img_dir'], fn)).convert('L'), dtype=float) / 255.
    return img[:_W['shape'][0], :_W['shape'][1]]


def kurtosis(x, axis=-1):
    m = x - x.mean(axis, keepdims=True)
    return (m**4).mean(axis) / (m**2).mean(axis)**2


def filter_kurtosis(img):
    """
    kurtosis of the linear responses (even & odd Gabor) of each filter (n_filters,),
    computed on the periodic component of the downsampled image (no boundary artifacts)
    """
    d = nim.downsample(img, nim.MODEL_DOWNSAMPLE)
    p, _ = nim.periodic_smooth(d - d.mean())
    R = np.fft.ifft2(np.fft.fft2(p)[None] * _W['filters'], axes=(-2, -1))
    R = R.reshape(len(R), -1)
    return 0.5 * (kurtosis(R.real) + kurtosis(R.imag))


def analyze_pair(args):
    i, j, fA, fB = args
    A, B = load_image(fA), load_image(fB)
    sA, sB = nim.phase_spectrum(A), nim.phase_spectrum(B)
    K = np.array([filter_kurtosis(nim.phase_morph(sA, sB, w)) for w in _W['ws']])
    K_orig = np.array([filter_kurtosis(nim.normalize(x)) for x in (A, B)])
    # phase-scrambled control: same (pair-mean) amplitude spectrum, random phases
    rng = np.random.default_rng(1000 * i + j)
    phi = np.angle(np.fft.fft2(rng.standard_normal(A.shape)))
    scrambled = np.real(np.fft.ifft2(0.5 * (sA[0] + sB[0]) * np.exp(1j * phi)))
    K_scr = filter_kurtosis(nim.normalize(scrambled))
    return i, j, K, K_orig, K_scr


# %% [markdown]
# ## Figures

# %%
def plot_pair(args):
    fn, fA, fB, naturalness, title = args
    A, B = load_image(fA), load_image(fB)
    sA, sB = nim.phase_spectrum(A), nim.phase_spectrum(B)
    ws = _W['ws']
    fig, AX = plt.subplots(1, len(ws) + 2, figsize=(14, 2.3))
    nim.show(AX[0], A[::2, ::2], 'original %s' % fA)
    for c, w in enumerate(ws):
        nim.show(AX[c + 1], nim.phase_morph(sA, sB, w)[::2, ::2],
                 'w = %.2f\nnaturalness %.2f' % (w, naturalness[c]))
    nim.show(AX[-1], B[::2, ::2], 'original %s' % fB)
    fig.suptitle(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(fn, dpi=100)
    plt.close(fig)


def plot_midpoints(rows, names, title):
    """ grid of the w=0.5 morph of the given pairs """
    n_col = 6
    n_row = int(np.ceil(len(rows) / n_col))
    fig, AX = plt.subplots(n_row, n_col, figsize=(2.3 * n_col, 1.95 * n_row), squeeze=False)
    for ax in AX.flat:
        ax.axis('off')
    for ax, r in zip(AX.flat, rows):
        A, B = load_image(names[r['i']]), load_image(names[r['j']])
        x = nim.phase_morph(nim.phase_spectrum(A), nim.phase_spectrum(B), 0.5)
        nim.show(ax, x[::2, ::2], '#%i  %s x %s\nmin naturalness %.2f' % (
            r['rank'], names[r['i']], names[r['j']], r['score']))
    fig.suptitle(title)
    fig.tight_layout()
    return fig


# %% [markdown]
# ## Main

# %%
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='naturalness (filter-response sparseness) of phase-morph continua for all image pairs')
    parser.add_argument('--img-dir', default=nim.IMG_DIR)
    parser.add_argument('--out-dir', default=os.path.join(nim.OUT_DIR, 'phase', 'naturalness'))
    parser.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    parser.add_argument('--max-pairs', type=int, default=None,
                        help='random subset of pairs (quick test), default: all pairs')
    parser.add_argument('--n-figures', type=int, default=None,
                        help='continuum figures for the n best pairs only, default: all, 0: none')
    args = parser.parse_args()

    ws = np.linspace(0, 1, N_W)
    interior = (ws > 0) & (ws < 1)

    files = nim.list_images(args.img_dir)
    names = [os.path.basename(f) for f in files]
    sizes = [Image.open(f).size for f in files]                 # (width, height), no pixel loading
    shape = (min(s[1] for s in sizes), min(s[0] for s in sizes))  # common (height, width)
    pairs = list(itertools.combinations(range(len(names)), 2))
    if args.max_pairs is not None and args.max_pairs < len(pairs):
        rng = np.random.default_rng(1)
        pairs = [pairs[k] for k in sorted(rng.choice(len(pairs), args.max_pairs, replace=False))]
    os.makedirs(os.path.join(args.out_dir, 'continuum'), exist_ok=True)
    print('%i images, %i pairs, %i morph weights, %i workers' % (
        len(names), len(pairs), N_W, args.workers))

    # --- sparseness of all continuum images
    t0 = time.time()
    results = {}
    with Pool(args.workers, initializer=init_worker, initargs=(args.img_dir, shape, ws)) as pool:
        tasks = [(i, j, names[i], names[j]) for i, j in pairs]
        for n, (i, j, K, K_orig, K_scr) in enumerate(pool.imap_unordered(analyze_pair, tasks, chunksize=4)):
            results[(i, j)] = (K, K_orig, K_scr)
            if (n + 1) % 50 == 0 or n + 1 == len(tasks):
                el = time.time() - t0
                print('sparseness: %i/%i pairs, %.0f min elapsed, %.0f min left' % (
                    n + 1, len(tasks), el / 60, el / (n + 1) * (len(tasks) - n - 1) / 60), flush=True)

    K = np.array([results[p][0] for p in pairs])            # (pairs, w, filters)
    K_orig = np.array([results[p][1] for p in pairs])       # (pairs, 2, filters)
    K_scr = np.array([results[p][2] for p in pairs])        # (pairs, filters)

    kurt = K.mean(-1)                                       # (pairs, w)
    kA, kB = K_orig.mean(-1).T
    k_scr = K_scr.mean(-1)
    k_nat = (1 - ws[None]) * kA[:, None] + ws[None] * kB[:, None]
    naturalness = (kurt - k_scr[:, None]) / np.maximum(k_nat - k_scr[:, None], MIN_CONTRAST)
    score = naturalness[:, interior].min(1)                 # least natural intermediate image
    order = np.argsort(-score)

    np.savez(os.path.join(args.out_dir, 'sparseness.npz'),
             names=np.array(names), pairs=np.array(pairs), ws=ws, sfs=np.array(SFS), n_ori=N_ORI,
             kurtosis=kurt, kurtosis_per_sf=K.reshape(len(pairs), N_W, len(SFS), N_ORI).mean(-1),
             kurtosis_A=kA, kurtosis_B=kB, kurtosis_scrambled=k_scr,
             naturalness=naturalness, score=score, order=order)

    # --- sorted table
    rows, header = [], ('rank,image_1,image_2,naturalness_min,naturalness_mean,naturalness_mid,'
                        'kurtosis_1,kurtosis_2,kurtosis_mid,kurtosis_scrambled,figure')
    mid = np.argmin(np.abs(ws - 0.5))
    for rank, p in enumerate(order, start=1):
        i, j = pairs[p]
        fig_name = 'rank-%05i_%s-%s.png' % (rank, *[os.path.splitext(names[k])[0] for k in (i, j)])
        rows.append(dict(rank=rank, i=i, j=j, p=p, score=score[p], fig=fig_name))
    with open(os.path.join(args.out_dir, 'pairs_sorted.csv'), 'w') as f:
        f.write(header + '\n')
        for r in rows:
            p = r['p']
            f.write('%i,%s,%s,%.4f,%.4f,%.4f,%.3f,%.3f,%.3f,%.3f,%s\n' % (
                r['rank'], names[r['i']], names[r['j']], score[p],
                naturalness[p, interior].mean(), naturalness[p, mid],
                kA[p], kB[p], kurt[p, mid], k_scr[p], r['fig']))
    print('best pairs:')
    for r in rows[:10]:
        print('  #%i  %s x %s  min naturalness %.2f' % (r['rank'], names[r['i']], names[r['j']], r['score']))

    # --- summary figures (main process)
    init_worker(args.img_dir, shape, ws)
    fig, AX = plt.subplots(1, 2, figsize=(9, 3.4))
    q25, q50, q75 = np.percentile(naturalness, [25, 50, 75], axis=0)
    AX[0].fill_between(ws, q25, q75, color=nim.SERIES['pixel'], alpha=0.15, lw=0)
    AX[0].plot(ws, q50, color=nim.SERIES['pixel'], lw=2, marker='o', ms=4)
    for y, lab in ((1, 'original images'), (0, 'phase-scrambled')):
        AX[0].axhline(y, color='0.6', lw=1, ls=':')
        AX[0].text(1.0, y, lab, ha='right', va='bottom', fontsize=7, color='0.4')
    AX[0].set_xlabel('morph weight w')
    AX[0].set_ylabel('naturalness index')
    AX[0].set_title('Filter-response sparseness (median, IQR, %i pairs)' % len(pairs), fontsize=9)
    AX[0].grid(color='0.92', lw=0.6)
    AX[1].hist(score, bins=50, color=nim.SERIES['pixel'], edgecolor='white', lw=0.5)
    AX[1].set_xlabel('min naturalness of intermediate images')
    AX[1].set_ylabel('number of pairs')
    AX[1].set_title('Pair score (used for ranking)', fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(args.out_dir, 'summary.png'), dpi=150)
    plt.close(fig)

    for which, sel in (('top', rows[:24]), ('bottom', rows[-12:])):
        fig = plot_midpoints(sel, names, '%s pairs by naturalness: midpoint (w = 0.5) images' % which.capitalize())
        fig.savefig(os.path.join(args.out_dir, '%s-pairs.png' % which), dpi=110)
        plt.close(fig)

    # --- continuum figures, named by rank (previous ones are removed: ranks change between runs)
    n_fig = len(rows) if args.n_figures is None else min(args.n_figures, len(rows))
    fig_dir = os.path.join(args.out_dir, 'continuum')
    for f in os.listdir(fig_dir):
        if f.startswith('rank-') and f.endswith('.png'):
            os.remove(os.path.join(fig_dir, f))
    t0 = time.time()
    with Pool(args.workers, initializer=init_worker, initargs=(args.img_dir, shape, ws)) as pool:
        tasks = [(os.path.join(fig_dir, r['fig']), names[r['i']], names[r['j']], naturalness[r['p']],
                  'rank %i / %i      %s x %s      min naturalness = %.2f' % (
                      r['rank'], len(rows), names[r['i']], names[r['j']], r['score']))
                 for r in rows[:n_fig]]
        for n, _ in enumerate(pool.imap_unordered(plot_pair, tasks, chunksize=4)):
            if (n + 1) % 100 == 0 or n + 1 == len(tasks):
                el = time.time() - t0
                print('figures: %i/%i, %.0f min elapsed, %.0f min left' % (
                    n + 1, len(tasks), el / 60, el / (n + 1) * (len(tasks) - n - 1) / 60), flush=True)

    print('done -> %s' % args.out_dir)
