# %% [markdown]
# # Project 5: Simulating an epidemic
#
# **Clinical question:** how do the contact rate, the duration of infection
# and vaccination coverage change the size and timing of an epidemic peak?
# Would the hospital be overwhelmed?
#
# **What you will build:**
# 1. The SIR model, solved step by step
# 2. The basic reproduction number $R_0$ and the epidemic threshold
# 3. Vaccination and herd immunity
# 4. Interventions (lockdown) and hospital capacity
# 5. (Optional) A stochastic version with individual patients
#
# Cells marked **TODO** are for you to complete.

# %%
import numpy as np
import matplotlib.pyplot as plt

# %% [markdown]
# ## 1. The SIR model
#
# The population of size $N$ is split into Susceptible, Infected and Recovered:
#
# $$ \frac{dS}{dt} = -\beta \frac{S I}{N}, \qquad
#    \frac{dI}{dt} = \beta \frac{S I}{N} - \gamma I, \qquad
#    \frac{dR}{dt} = \gamma I $$
#
# - $\beta$: number of transmitting contacts per infected person per day
# - $\gamma = 1 / D$, with $D$ the duration of infectiousness (days)

# %%
def simulate_sir(beta, gamma, N=1_000_000, I0=10, R0_init=0,
                 t_max=200, dt=0.1):
    t = np.arange(0, t_max, dt)
    S, I, R = np.zeros(len(t)), np.zeros(len(t)), np.zeros(len(t))
    S[0], I[0], R[0] = N - I0 - R0_init, I0, R0_init
    for i in range(1, len(t)):
        new_infections = beta * S[i-1] * I[i-1] / N * dt
        new_recoveries = gamma * I[i-1] * dt
        S[i] = S[i-1] - new_infections
        I[i] = I[i-1] + new_infections - new_recoveries
        R[i] = R[i-1] + new_recoveries
    return t, S, I, R

def plot_sir(t, S, I, R, ax=None, title=''):
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(t, S, label='susceptible')
    ax.plot(t, I, label='infected')
    ax.plot(t, R, label='recovered')
    ax.set_xlabel('time (days)')
    ax.set_ylabel('people')
    ax.set_title(title)
    ax.legend(fontsize=8)
    return ax

t, S, I, R = simulate_sir(beta=0.3, gamma=1/7)
plot_sir(t, S, I, R, title='β = 0.3, D = 7 days')

# %% [markdown]
# **TODO:** Check that $S + I + R$ stays equal to $N$ at all times.
# Find the day of the peak and the number of people infected at the peak
# (`np.argmax`). What fraction of the population is never infected?

# %%
# TODO

# %% [markdown]
# ## 2. The basic reproduction number
#
# $R_0 = \beta / \gamma$ is the average number of people infected by one
# case in a fully susceptible population.
#
# **TODO:** Run the model for $R_0$ from 0.5 to 5 and plot the final
# epidemic size (fraction ever infected) against $R_0$. What happens around
# $R_0 = 1$?

# %%
gamma = 1/7
R0_values = np.linspace(0.5, 5, 30)
final_size = []
for R0 in R0_values:
    t, S, I, R = simulate_sir(beta=R0 * gamma, gamma=gamma, t_max=500)
    final_size.append(R[-1] / 1_000_000)

fig, ax = plt.subplots(figsize=(5, 3))
ax.plot(R0_values, final_size, 'o-')
ax.set_xlabel('$R_0$')
ax.set_ylabel('fraction ever infected')

# %% [markdown]
# ## 3. Vaccination
#
# Vaccinated people are immune from the start: they go directly into $R$.
#
# **TODO:** Use the `R0_init` argument to simulate a vaccination coverage
# from 0 to 100 %, for $R_0 = 3$. Plot the peak number of infected and the
# final size against coverage. Compare the coverage needed to prevent the
# epidemic with the theoretical herd immunity threshold $1 - 1/R_0$.

# %%
# TODO

# %% [markdown]
# ## 4. Lockdown and hospital capacity
#
# Assume 5 % of infected people need a hospital bed, and the region has
# 3 000 beds.
#
# **TODO:** Modify the simulation so that $\beta$ depends on time: it is
# divided by a factor (e.g. 3) between day `t_start` and day `t_end`.
# Find a lockdown start and duration that keep hospital occupancy below
# capacity. What happens when the lockdown is lifted too early?

# %%
hospital_fraction = 0.05
hospital_beds = 3000

def simulate_sir_lockdown(beta, gamma, t_start, t_end, reduction=3, **kwargs):
    # TODO: copy simulate_sir and make beta time dependent
    return simulate_sir(beta, gamma, **kwargs)

t, S, I, R = simulate_sir_lockdown(beta=0.3, gamma=1/7, t_start=30, t_end=90)
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(t, hospital_fraction * I, label='hospitalised')
ax.axhline(hospital_beds, color='r', ls='--', label='capacity')
ax.set_xlabel('time (days)')
ax.set_ylabel('beds needed')
ax.legend()

# %% [markdown]
# ## 5. (Optional) A stochastic epidemic
#
# In a small population (a nursing home of 100 residents), chance matters:
# an outbreak can die out early even with $R_0 > 1$.
#
# **TODO:** At each time step, draw the number of new infections and
# recoveries at random with `np.random.binomial`:
# - each susceptible is infected with probability $\beta \, I / N \, dt$
# - each infected recovers with probability $\gamma \, dt$
#
# Run 200 simulations starting from a single case and plot the histogram of
# final sizes. What fraction of outbreaks die out by themselves? Compare
# with the theoretical value $1 / R_0$.
#
# **Questions for your report:**
# - Which assumptions of the SIR model are unrealistic for a real disease?
# - Which parameter would you most like to know precisely at the start of
#   an epidemic, and why?
