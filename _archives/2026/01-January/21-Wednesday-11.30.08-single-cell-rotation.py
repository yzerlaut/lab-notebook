import time
import matplotlib.pylab as plt
import plot_tools as pt
import numpy as np


fig, ax = pt.figure(ax_scale=(2,2))

line, = ax.plot(np.arange(100), np.random.randn(100), 'ko', ms=2)

for i in range(10):

    line.set_ydata(np.random.randn(100))
    plt.pause(0.5)

plt.ioff()

