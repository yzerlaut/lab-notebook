# %%
import sys
import numpy as np
sys.path += ['physion/src']

from physion.utils import plot_tools as pt 

# pt.set_style('dark')

# %%
from physion.ephys.tools import compute_freq_envelope

t = np.linspace(0, 11, int(5e4))
signal = np.zeros(len(t))

np.random.seed(11)
N = 20
for freq, start, amp in zip(
    list(np.random.uniform(0.5, 20, N)), list(1+np.arange(N)/N*9), list(np.random.randn(N)),
    ):
    sigma = 1./freq/2.
    signal += np.sin(2*np.pi*freq*(t-start))*\
        np.exp(-(t-start)**2/2./sigma**2)*\ amp

fig, ax = pt.figure(axes=(1,4), ax_scale=(2,1.5))
ax[0].plot(t, signal)
pt.set_plot(ax[0], xlabel='time (s)', ylabel='signal (a.u.)')
for i, band in enumerate([[5,20], [1,10], [0.2,1]]):
    mua = compute_freq_envelope(signal, 1./(t[1]-t[0]),
                    np.linspace(band[0], band[1], 5))
    ax[i+1].fill_between(t, 0*t, mua)
    pt.set_plot(ax[i+1], xlabel='time (s)', ylabel='envelope (a.u.)',
                    title='freq. band: [%.1f,%.1f]Hz' % tuple(band) +\
                        40*'  ')
fig.savefig('physion/docs/ephys/wavelet-envelope.png')
# %%
