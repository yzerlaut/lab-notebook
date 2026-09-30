# COPY DATA/Ste-Zucca/Wild_Type
#           in ~/DATA/Ste-Zucca/Wild_Type

# %%
import pyabf, os, sys
import plot_tools as pt
import numpy as np

folder = os.path.join(os.path.expanduser('~'), 'DATA', 'Ste-Zucca', 'Wild_Type')
files = np.sort([[os.path.join(folder, f, ff) for ff in os.listdir(os.path.join(folder, f)) if ('.abf' in ff) and (ff[0]!='.')][0] for f in os.listdir(folder)])

def load(f):
    abf = pyabf.ABF(f)
    dt = 1./abf.dataRate
    Vm = abf.data[1,:]
    t = np.arange(abf.data.shape[1])*dt
    return t, Vm

# %%
# SEE ALL CELLS
t0, width = 5*60, 120
for i, f in enumerate(files):
    t, Vm = load(f)
    cond  = (t>t0) & (t<t0+width)
    fig, ax = pt.figure(ax_scale=(2.5,1.5))
    ax.set_title('%i), %s' % (i, f.split(os.path.sep)[-2]))
    ax.plot(t[cond], Vm[cond], lw=0.5)
    pt.draw_bar_scales(Xbar=0.5, Xbar_label='500ms', Ybar=20, Ybar_label='20mV', ax=ax)
    ax.axis('off')

# %%
# SEE ALL EPOCHS (of a given cell)
t, Vm = load(files[5])
t0, width = 0, 20

for t0 in width*np.arange(int(t[-1]/width)):
    cond  = (t>t0) & (t<t0+width)
    fig, ax = pt.figure(ax_scale=(2.5,1.5))
    ax.set_title('$t_0$=%.1fs' % t0)
    ax.plot(t[cond], Vm[cond], lw=0.5)
    pt.draw_bar_scales(Xbar=0.5, Xbar_label='500ms', Ybar=20, Ybar_label='20mV', ax=ax)
    ax.axis('off')

# %%
t, Vm = load(files[5])
t0, width = 1766, 20 
cond  = (t>t0) & (t<t0+width)
fig, ax = pt.figure(ax_scale=(2.3,2.2))
ax.plot(t[cond], Vm[cond], lw=0.5)
pt.draw_bar_scales(Xbar=1, Xbar_label='1s', Ybar=20, Ybar_label=' 20mV ', ax=ax)
ax.axis('off')
pt.save(fig)

# %%
t, Vm = load(files[12])
t0, width = 1948, 3  # zoom on burst spiking
cond  = (t>t0) & (t<t0+width)
fig, ax = pt.figure(ax_scale=(2.3,2.2))
ax.plot(t[cond], Vm[cond], lw=0.5)
pt.draw_bar_scales(Xbar=1, Xbar_label='1s', Ybar=20, Ybar_label=' 20mV ', ax=ax)
ax.axis('off')

# %%
