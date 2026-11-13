# %% [markdown]
# # Project 3: A heart rate monitor from a raw ECG
#
# **Clinical question:** from a raw ECG recording, can we measure heart rate,
# heart rate variability, and automatically detect abnormal rhythms?
#
# **Data:** 5 minutes of a real ECG (MIT-BIH Arrhythmia Database, record 208,
# sampled at 360 Hz), shipped with SciPy. Record 208 contains many premature
# ventricular contractions (PVCs), which makes it interesting.
#
# **What you will build:**
# 1. Load and plot an ECG
# 2. Filter the signal
# 3. Detect R peaks
# 4. Compute heart rate and RR interval statistics
# 5. Flag tachycardia, bradycardia and irregular beats
#
# Cells marked **TODO** are for you to complete.

# %%
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# %% [markdown]
# ## 1. Load the ECG
#
# `scipy.datasets.electrocardiogram()` needs the `pooch` package
# (`pip install pooch`) and an internet connection the first time.

# %%
from scipy.datasets import electrocardiogram

ecg = electrocardiogram()   # in mV
fs = 360                    # sampling frequency (Hz)
t = np.arange(len(ecg)) / fs

print(f'{len(ecg)} samples, duration = {t[-1]:.1f} s')

fig, ax = plt.subplots(figsize=(8, 2.5))
ax.plot(t, ecg, lw=0.8)
ax.set_xlim(0, 10)
ax.set_xlabel('time (s)')
ax.set_ylabel('ECG (mV)')

# %% [markdown]
# **TODO:** Look at different 10 s windows (`ax.set_xlim`). Identify the P wave,
# the QRS complex and the T wave. Can you spot a PVC (wide, abnormal QRS)?

# %% [markdown]
# ## 2. Filter the signal
#
# The raw ECG contains a slow baseline drift (breathing, movement) and
# high-frequency noise. A band-pass filter between 0.5 and 40 Hz removes both.

# %%
def bandpass(x, fs, low=0.5, high=40, order=3):
    b, a = signal.butter(order, [low, high], btype='bandpass', fs=fs)
    return signal.filtfilt(b, a, x)

ecg_filtered = bandpass(ecg, fs)

fig, ax = plt.subplots(figsize=(8, 2.5))
ax.plot(t, ecg, lw=0.8, label='raw')
ax.plot(t, ecg_filtered, lw=0.8, label='filtered')
ax.set_xlim(0, 10)
ax.set_xlabel('time (s)')
ax.legend()

# %% [markdown]
# ## 3. Detect R peaks
#
# The R peak is the tallest, sharpest deflection of each beat. A simple
# detector: find local maxima above a threshold, separated by at least a
# refractory period (no two beats closer than 250 ms, i.e. > 240 bpm).

# %%
def detect_r_peaks(x, fs, threshold=None, refractory=0.25):
    if threshold is None:
        # TODO: try other ways to choose the threshold automatically
        threshold = 0.5 * np.max(x)
    peaks, _ = signal.find_peaks(x, height=threshold,
                                 distance=int(refractory * fs))
    return peaks

peaks = detect_r_peaks(ecg_filtered, fs)
print(f'{len(peaks)} beats detected')

fig, ax = plt.subplots(figsize=(8, 2.5))
ax.plot(t, ecg_filtered, lw=0.8)
ax.plot(t[peaks], ecg_filtered[peaks], 'r.', ms=8)
ax.set_xlim(0, 10)
ax.set_xlabel('time (s)')

# %% [markdown]
# **TODO:** Check the detection over the whole recording. Are some beats missed?
# Are some T waves wrongly detected? A single large artefact can ruin a
# threshold based on `np.max`: try a percentile instead (`np.percentile`).
#
# **Going further:** implement a simplified Pan-Tompkins detector
# (derivative, squaring, moving-window integration, then threshold).

# %% [markdown]
# ## 4. Heart rate and RR intervals

# %%
rr = np.diff(peaks) / fs      # RR intervals, in seconds
hr = 60 / rr                  # instantaneous heart rate, in bpm
t_beats = t[peaks[1:]]

print(f'Mean heart rate: {np.mean(hr):.0f} bpm')

fig, AX = plt.subplots(1, 2, figsize=(9, 3))
AX[0].plot(t_beats, hr, '.-', lw=0.5)
AX[0].set_xlabel('time (s)')
AX[0].set_ylabel('heart rate (bpm)')
AX[1].hist(rr * 1000, bins=50)
AX[1].set_xlabel('RR interval (ms)')
AX[1].set_ylabel('beats')
fig.tight_layout()

# %% [markdown]
# **TODO:** Compute the standard heart rate variability measures:
# - SDNN: standard deviation of RR intervals (ms)
# - RMSSD: root mean square of successive RR differences (ms)
#
# Plot a Poincaré map: each RR interval against the next one
# (`rr[:-1]` vs `rr[1:]`). What do the clusters away from the diagonal mean?

# %%
def sdnn(rr):
    # TODO
    return np.nan

def rmssd(rr):
    # TODO
    return np.nan

# %% [markdown]
# ## 5. Automatic alarms
#
# **TODO:** Write a function that scans the recording with a sliding window
# (for example 10 s) and returns, for each window, a label among
# `'normal'`, `'bradycardia'` (< 60 bpm), `'tachycardia'` (> 100 bpm).
#
# Then flag *premature beats*: a beat whose RR interval is much shorter
# (e.g. < 80 %) than the median of the surrounding beats, followed by a
# compensatory pause. Mark them in red on the ECG plot.

# %%
def rhythm_labels(peaks, fs, window=10):
    # TODO
    return []

def premature_beats(rr, ratio=0.8, n_neighbours=5):
    # TODO: return the indices of premature beats
    return np.array([], dtype=int)

# %% [markdown]
# **Questions for your report:**
# - How many PVCs did you detect? How confident are you in that number?
# - Why must a clinical heart monitor have very few false alarms?
#   And very few missed events? Can it have both?
# - (Going further) The full MIT-BIH database has expert beat annotations.
#   With `pip install wfdb` you can load record 208 and its annotations
#   (`wfdb.rdann('208', 'atr', pn_dir='mitdb')`) to measure the sensitivity
#   of your detector.
