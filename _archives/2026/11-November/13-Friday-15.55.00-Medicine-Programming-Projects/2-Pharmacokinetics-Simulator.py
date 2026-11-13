# %% [markdown]
# # Project 2: A pharmacokinetics simulator
#
# **Clinical question:** for a given drug, which dose and dosing interval keep
# the plasma concentration inside the therapeutic window?
#
# **What you will build:**
# 1. A one-compartment model with intravenous bolus injection
# 2. Repeated dosing, and the approach to steady state
# 3. Oral administration (absorption from the gut)
# 4. A search for the best dosing regimen
# 5. (Optional) Patient variability: renal failure, body weight
#
# Cells marked **TODO** are for you to complete.

# %%
import numpy as np
import matplotlib.pyplot as plt

# %% [markdown]
# ## 1. The one-compartment model
#
# The body is a single well-mixed compartment of volume $V$ (litres).
# The drug is eliminated at a rate proportional to its concentration $C$:
#
# $$ \frac{dC}{dt} = -k_e \, C $$
#
# with $k_e = \ln(2) / t_{1/2}$, where $t_{1/2}$ is the elimination half-life.
# After an intravenous bolus of dose $D$ (mg), $C(0) = D / V$.
#
# We solve this equation numerically, step by step (Euler method):
# $C(t + dt) = C(t) - k_e \, C(t) \, dt$

# %%
# Parameters loosely based on gentamicin (an aminoglycoside antibiotic)
drug = {
    'name': 'gentamicin-like',
    'half_life': 2.5,         # hours
    'volume': 0.25 * 70,      # litres (0.25 L/kg for a 70 kg patient)
    'C_min_effective': 1.0,   # mg/L, below this the drug is not effective
    'C_max_toxic': 10.0,      # mg/L, above this the drug becomes toxic
}

def simulate_single_bolus(dose, drug, t_max=24, dt=0.01):
    k_e = np.log(2) / drug['half_life']
    t = np.arange(0, t_max, dt)
    C = np.zeros(len(t))
    C[0] = dose / drug['volume']
    for i in range(1, len(t)):
        C[i] = C[i-1] - k_e * C[i-1] * dt
    return t, C

t, C = simulate_single_bolus(dose=120, drug=drug)

def plot_concentration(t, C, drug, ax=None, label=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 3))
    ax.axhspan(drug['C_min_effective'], drug['C_max_toxic'],
               color='tab:green', alpha=0.15, label='therapeutic window')
    ax.plot(t, C, label=label)
    ax.set_xlabel('time (h)')
    ax.set_ylabel('concentration (mg/L)')
    ax.legend(loc='upper right', fontsize=8)
    return ax

plot_concentration(t, C, drug, label='120 mg IV bolus')

# %% [markdown]
# **TODO:** The exact solution is $C(t) = C(0) \, e^{-k_e t}$.
# Plot it on top of the numerical solution. What happens if you increase `dt`
# to 0.5 h? to 2 h?

# %%
# TODO

# %% [markdown]
# ## 2. Repeated dosing
#
# The patient now receives a dose every `interval` hours.

# %%
def simulate_repeated_bolus(dose, interval, drug, t_max=72, dt=0.01):
    k_e = np.log(2) / drug['half_life']
    t = np.arange(0, t_max, dt)
    C = np.zeros(len(t))
    dose_times = np.arange(0, t_max, interval)
    for i in range(1, len(t)):
        C[i] = C[i-1] - k_e * C[i-1] * dt
        # TODO: is there a dose given between t[i-1] and t[i]?
        for td in dose_times:
            if t[i-1] < td <= t[i]:
                C[i] += dose / drug['volume']
    C[0] = dose / drug['volume']
    return t, C

fig, ax = plt.subplots(figsize=(6, 3))
for interval in [4, 8, 12]:
    t, C = simulate_repeated_bolus(dose=120, interval=interval, drug=drug)
    plot_concentration(t, C, drug, ax=ax, label=f'every {interval} h')

# %% [markdown]
# **TODO:**
# - How long does it take to reach steady state? Relate it to the half-life.
# - Compute, for each regimen, the fraction of time spent in the therapeutic
#   window, below it, and above it.

# %%
def time_in_window(C, drug):
    # TODO: return the fractions of time below, inside and above the window
    inside = np.mean((C >= drug['C_min_effective']) & (C <= drug['C_max_toxic']))
    return inside

# %% [markdown]
# ## 3. Oral administration
#
# With an oral dose, the drug first sits in the gut (amount $A$, mg) and is
# absorbed at rate $k_a$, with bioavailability $F$ (fraction reaching blood):
#
# $$ \frac{dA}{dt} = -k_a A, \qquad
#    \frac{dC}{dt} = \frac{k_a A}{V} - k_e C $$
#
# with $A(0) = F \times D$.

# %%
def simulate_oral(dose, interval, drug, k_a=1.0, F=0.8, t_max=72, dt=0.01):
    # TODO: implement the two equations above, with repeated doses
    # added to the gut compartment A
    t = np.arange(0, t_max, dt)
    C = np.zeros(len(t))
    return t, C

# %% [markdown]
# **TODO:** Compare IV and oral administration of the same dose.
# How do the peak concentration and the time of the peak change with $k_a$?

# %% [markdown]
# ## 4. Find the best dosing regimen
#
# **TODO:** Loop over a grid of doses and intervals, compute the time spent in
# the therapeutic window at steady state (for example the last 24 h), and
# display the result as a 2D map with `plt.imshow` or `plt.pcolormesh`.
# Which regimen would you prescribe? Is it practical for the patient?

# %%
doses = np.arange(40, 401, 40)       # mg
intervals = np.array([4, 6, 8, 12, 24])  # hours
score = np.zeros((len(doses), len(intervals)))

for i, dose in enumerate(doses):
    for j, interval in enumerate(intervals):
        t, C = simulate_repeated_bolus(dose, interval, drug, t_max=96)
        steady = t > 72
        score[i, j] = time_in_window(C[steady], drug)

fig, ax = plt.subplots(figsize=(4, 4))
im = ax.imshow(score, origin='lower', aspect='auto', cmap='viridis')
ax.set_xticks(range(len(intervals)), intervals)
ax.set_yticks(range(len(doses)), doses)
ax.set_xlabel('interval (h)')
ax.set_ylabel('dose (mg)')
fig.colorbar(im, label='fraction of time in window')

# %% [markdown]
# ## 5. (Optional) Patient variability
#
# - Body weight changes the volume of distribution $V$.
# - Renal failure lengthens the half-life of renally cleared drugs
#   (gentamicin's half-life can exceed 24 h in severe renal failure).
#
# **TODO:** Write a function `make_patient(weight, creatinine_clearance)` that
# returns adapted drug parameters, and show how the optimal regimen changes.
# Then simulate 100 patients with random weights and clearances: what fraction
# of them ends up in the toxic range with a "one size fits all" regimen?
#
# **Questions for your report:**
# - Why do hospitals measure trough (pre-dose) levels of gentamicin?
# - What are the limits of a one-compartment model?
