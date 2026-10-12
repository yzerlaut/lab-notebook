# %% [markdown]
# # Minimal propagation model on a ring
#
# Simplified version of the "ring model" of Zerlaut et al., J. Comput. Neurosci. (2018):
# a neural field with first-order temporal dynamics and delayed lateral interactions.
#
# For each position $x$ on a ring of circumference $L$:
#
# $$ \tau \, \frac{dV}{dt} = -V \;-\; a \;+\; J \, \int w(x-y) \; F\Big[V\big(y, t - \tfrac{d(x,y)}{c}\big)\Big] \, dy \;+\; I_{ext}(x,t) $$
#
# $$ \tau_a \, \frac{da}{dt} = -a + k_a \, V $$
#
# with:
# - **RC-like integration**: the leak term $-V$ with time constant $\tau$
# - **tanh amplification**: $F(V) = \tfrac{1}{2}\big[1+\tanh\big((V-\theta)/\delta\big)\big]$, a threshold non-linearity
# - **adaptation**: $a$ follows $V$ slowly and inactivates the site after strong activity
#   (with an undershoot below baseline before the recovery)
# - **spatial interactions**: Gaussian connectivity $w(d) \propto \exp(-d^2/2\sigma_w^2)$ (normalized to $\int w = 1$)
#   with propagation delays $d(x,y)/c$, where $d$ is the distance along the ring and $c$ the propagation speed
# - **input**: a Gaussian waveform in space and time $I_{ext}(x,t) = A \, e^{-(x-x_0)^2/2\sigma_x^2} \, e^{-(t-t_0)^2/2\sigma_t^2}$
#
# Units: space in mm, time in s (so speeds are in mm/s).

# %%
import sys, os
import numpy as np
sys.path += ['./']
import plot_tools as pt

# %%
def gaussian(x, x0=0, sx=1):
    return np.exp(-(x-x0)**2/2./sx**2)

def F(V, theta=0.5, delta=0.15):
    """ non-linear amplification: tanh-based threshold function, in [0,1] """
    return 0.5*(1+np.tanh((V-theta)/delta))

default_params = dict(
    # ring
    L=20.,          # mm, ring circumference
    N=200,          # number of sites
    # temporal dynamics
    tau=0.1,        # s, RC-like integration time constant
    theta=0.5,      # threshold of the tanh non-linearity
    delta=0.25,     # width of the tanh non-linearity
    tau_a=0.8,      # s, adaptation time constant
    k_a=3.3,         # adaptation strength (k_a > J/theta-1 for the activity to switch off)
    # spatial interactions
    J=3.,           # recurrent coupling strength
    sigma_w=0.6,    # mm, extent of the Gaussian connectivity
    c=20.,          # mm/s, propagation speed of the lateral interactions
    # input
    A=1.5,          # amplitude
    x0=0.,          # mm, center of the stimulus
    sx=0.5,         # mm, spatial extent
    t0=0.3,         # s, time of peak
    st=0.08,        # s, temporal extent
    # simulation
    tstop=3.,       # s
    dt=1e-3,        # s
)

# %% [markdown]
# ## Model implementation

# %%
def build_ring(p):
    """ positions, distances along the ring, connectivity and delays (in time steps) """
    dx = p['L']/p['N']
    x = np.arange(p['N'])*dx - p['L']/2.  # positions in [-L/2, L/2[
    dist = np.abs(x[:,np.newaxis]-x[np.newaxis,:])
    dist = np.minimum(dist, p['L']-dist)  # shortest path on the ring
    W = gaussian(dist, sx=p['sigma_w'])
    W /= W.sum(axis=1, keepdims=True)  # normalized: a uniform activity F gives an input J*F
    delays = np.round(dist/p['c']/p['dt']).astype(int)
    return x, dist, W, delays

def run_sim(p=default_params):
    p = {**default_params, **p}
    x, dist, W, delays = build_ring(p)
    t = np.arange(int(p['tstop']/p['dt']))*p['dt']

    V, a = np.zeros((len(t), p['N'])), np.zeros((len(t), p['N']))
    Iext = p['A']*gaussian(t, p['t0'], p['st'])[:,np.newaxis]*\
                    gaussian(x, p['x0'], p['sx'])[np.newaxis,:]

    # circular buffer of the past F(V) values, long enough for the maximum delay
    Nbuffer = delays.max()+1
    Fbuffer = np.ones((Nbuffer, p['N']))*F(0, p['theta'], p['delta'])
    J = np.arange(p['N'])[np.newaxis,:]

    for it in range(len(t)-1):
        Fbuffer[it%Nbuffer,:] = F(V[it,:], p['theta'], p['delta'])
        # delayed presynaptic activity: F[V(y, t-d(x,y)/c)] for each (x,y) pair
        Fdelayed = Fbuffer[(it-delays)%Nbuffer, J]
        Irec = p['J']*np.sum(W*Fdelayed, axis=1)
        V[it+1,:] = V[it,:] + p['dt']/p['tau']*(-V[it,:]-a[it,:]+Irec+Iext[it,:])
        a[it+1,:] = a[it,:] + p['dt']/p['tau_a']*(-a[it,:]+p['k_a']*V[it,:])

    return dict(t=t, x=x, V=V, a=a, Iext=Iext, W=W, dist=dist, params=p)

# %% [markdown]
# ## Simulation

# %%
sim = run_sim()

# %% [markdown]
# ## Model components: non-linearity, connectivity, delays

# %%
p = sim['params']
fig, AX = pt.figure(axes=(3,1), wspace=2.)

v = np.linspace(-0.5, 1.5, 100)
AX[0].plot(v, F(v, p['theta'], p['delta']), 'k-')
pt.set_plot(AX[0], xlabel='$V$', ylabel='$F(V)$', title='non-linearity')

d = np.linspace(-3*p['sigma_w'], 3*p['sigma_w'], 100)
AX[1].plot(d, gaussian(d, sx=p['sigma_w']), 'k-')
pt.set_plot(AX[1], xlabel='distance (mm)', ylabel='$w$ (norm.)', title='connectivity')

d = np.linspace(0, p['L']/2, 100)
AX[2].plot(d, d/p['c'], 'k-')
pt.set_plot(AX[2], xlabel='distance (mm)', ylabel='delay (s)', title='c=%imm/s' % p['c'])

# %% [markdown]
# ## Spatio-temporal dynamics

# %%
def show_map(ax, Z, t, x, cmap=pt.plt.cm.bwr):
    """ space-time map with a diverging colormap centered on the baseline (0) """
    vmax = np.abs(Z).max()
    ax.imshow(Z.T, origin='lower', aspect='auto', cmap=cmap, vmin=-vmax, vmax=vmax,
              extent=[t[0], t[-1], x[0], x[-1]])
    return vmax

def plot_dynamics(sim, cmap=pt.plt.cm.viridis):
    t, x, V, a = sim['t'], sim['x'], sim['V'], sim['a']
    p = sim['params']
    fig, AX = pt.figure(axes=(3,1), ax_scale=(1.,1.2), wspace=2.)

    for ax, Z, label in zip(AX[:2], [sim['Iext'], V], ['input $I_{ext}$', '$\\delta$ act.']):
        vmax = show_map(ax, Z, t, x)
        pt.set_plot(ax, xlabel='time (s)', ylabel='space (mm)', title=label)

    # bar legend of the activity map
    pt.bar_legend(AX[1], continuous=True, colormap=pt.plt.cm.bwr,
                  colorbar_inset=dict(rect=[1.05,.1,.05,.8], facecolor=None),
                  bounds=[-vmax, vmax], ticks=[-np.floor(vmax), 0, np.floor(vmax)])

    # traces at increasing distances from the stimulus, positions marked on the map
    distances = np.linspace(0, p['L']/2.*0.8, 5)
    for i, d in enumerate(distances):
        ix = np.argmin(np.abs(x-p['x0']-d))
        color = cmap(i/(len(distances)-1))
        AX[1].axhline(x[ix], color=color, lw=0.3)
        AX[2].plot(t, V[:,ix], color=color, label='%.1fmm' % d)
    AX[2].plot(t, a[:,np.argmin(np.abs(x-p['x0']))], 'k:', lw=0.5, label='$a$ @ 0mm')
    pt.set_plot(AX[2], xlabel='time (s)', ylabel='$\\delta$ act.', title='traces')
    AX[2].legend(loc='upper right', frameon=False, fontsize=6)
    return fig, AX

fig, AX = plot_dynamics(sim)
pt.save(fig)
# %% [markdown]
# ## Effect of the propagation speed

# %%
fig, AX = pt.figure(axes=(3,1), ax_scale=(1.3,2.), wspace=0.5)
for ax, c in zip(AX, [10, 30, 100]):
    s = run_sim(dict(c=c))
    show_map(ax, s['V'], s['t'], s['x'])
    pt.set_plot(ax, xlabel='time (s)', ylabel='space (mm)' if ax is AX[0] else '',
                yticks_labels=None if ax is AX[0] else [], title='c=%imm/s' % c)

# %% [markdown]
# ## Effect of the coupling strength: damped spread vs. regenerative wave

# %%
fig, AX = pt.figure(axes=(3,1), ax_scale=(1.3,2.), wspace=0.5)
for ax, J in zip(AX, [1., 2., 3.]):
    s = run_sim(dict(J=J))
    show_map(ax, s['V'], s['t'], s['x'])
    pt.set_plot(ax, xlabel='time (s)', ylabel='space (mm)' if ax is AX[0] else '',
                yticks_labels=None if ax is AX[0] else [], title='J=%.1f' % J)

# %%
# %% [markdown]
# ## Schematic: Gaussian connectivity on the ring (SVG)

# %%
def ring_connectivity_svg(filename='ring-connectivity.svg',
                          Nsites=36, sigma_deg=35., R=120., bump=55.,
                          color='#d62728', target_deg=70.):
    """
    draws the ring of sites, the connections of one reference site (top)
    weighted by the gaussian profile, the profile as a bump around the ring,
    and the distance / delay to one target site
    (schematic: sigma is exaggerated with respect to the model parameters)
    """
    W, H = 2*(R+bump+45), 2*(R+bump+45)
    cx, cy = W/2, H/2
    pol = lambda r, deg: (cx+r*np.sin(np.radians(deg)), cy-r*np.cos(np.radians(deg)))
    w = lambda deg: gaussian((deg+180)%360-180, sx=sigma_deg)  # angle from the top site

    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%i" height="%i" viewBox="0 0 %i %i" font-family="Helvetica, Arial, sans-serif">' % (W, H, W, H),
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker></defs>']

    # gaussian profile as a bump around the ring
    angles = np.linspace(-180, 180, 361)
    outer = ' '.join('%.1f,%.1f' % pol(R+bump*w(a), a) for a in angles)
    inner = ' '.join('%.1f,%.1f' % pol(R, a) for a in angles[::-1])
    svg.append('<g id="profile"><polygon points="%s %s" fill="%s" fill-opacity="0.15" stroke="none"/>' % (outer, inner, color))
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5"/></g>' % (outer, color))

    # ring
    svg.append('<circle id="ring" cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#999" stroke-width="2"/>' % (cx, cy, R))

    # connections from the reference site, width and opacity ~ w(d)
    svg.append('<g id="connections" stroke="%s" stroke-linecap="round">' % color)
    x0, y0 = pol(R, 0)
    for a in np.arange(1, Nsites)*360./Nsites:
        if w(a)>0.02:
            x1, y1 = pol(R, a)
            svg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke-width="%.2f" stroke-opacity="%.2f"/>' % (x0, y0, x1, y1, 4*w(a), w(a)))
    svg.append('</g>')

    # sites
    svg.append('<g id="sites">')
    for a in np.arange(Nsites)*360./Nsites:
        x1, y1 = pol(R, a)
        svg.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="white" stroke-width="1"/>' % (x1, y1, 6 if a==0 else 4, 'black' if a==0 else '#666'))
    svg.append('</g>')

    # sigma_w annotation, along the bump at half height
    a_sig = sigma_deg
    xs, ys = pol(R+bump*w(a_sig)+18, 0)
    svg.append('<g id="sigma"><path d="M%.1f,%.1f A%.1f,%.1f 0 0,1 %.1f,%.1f" fill="none" stroke="#333" stroke-width="1" marker-end="url(#arrow)"/>' % (
        *pol(R+bump+12, 0), R+bump+12, R+bump+12, *pol(R+bump+12, a_sig)))
    svg.append('<text x="%.1f" y="%.1f" font-size="14" fill="#333">σ<tspan font-size="10" dy="3">w</tspan></text></g>' % (*pol(R+bump+22, a_sig/2),))

    # distance and delay to a target site, along the inside of the ring
    r_in = R-18
    xt, yt = pol(R, target_deg)
    svg.append('<g id="delay"><circle cx="%.1f" cy="%.1f" r="5" fill="none" stroke="black" stroke-width="1.5"/>' % (xt, yt))
    svg.append('<path d="M%.1f,%.1f A%.1f,%.1f 0 0,1 %.1f,%.1f" fill="none" stroke="#333" stroke-width="1" stroke-dasharray="3,2" marker-start="url(#arrow)" marker-end="url(#arrow)"/>' % (
        *pol(r_in, 4), r_in, r_in, *pol(r_in, target_deg-4)))
    xl, yl = pol(r_in-30, target_deg/2)
    svg.append('<text x="%.1f" y="%.1f" font-size="14" fill="#333" text-anchor="middle">d</text>' % (xl, yl))
    svg.append('<text x="%.1f" y="%.1f" font-size="13" fill="#333" text-anchor="middle">delay = d / c</text></g>' % (cx, cy+5))

    # labels
    svg.append('<text x="%.1f" y="%.1f" font-size="13" fill="%s" text-anchor="middle">w(d)</text>' % (*pol(R+bump+22, -a_sig), color))
    svg.append('</svg>')

    with open(filename, 'w') as f:
        f.write('\n'.join(svg))
    print('[ok] schematic saved as', filename)

ring_connectivity_svg()

# %%
