# %% [markdown]
# # Overfitting through hyperparameter selection
#
# **Message of this notebook:** a validation set protects you against
# overfitting the *parameters* of a model (the weights learnt on the training
# set). It does **not** protect you against overfitting the *hyperparameters*:
# as soon as you use the validation score to make a choice, that score is no
# longer an honest estimate of performance.
#
# This is the "winner's curse": if you try many settings and keep the best
# one, you mostly select the one that was *lucky* on the validation set.
#
# **Plan:**
# 1. A dataset where labels are pure noise: any accuracy above 50% is an illusion
# 2. Grid search on a validation set: the best score looks great...
# 3. ...and collapses on an untouched test set
# 4. The more settings you try, the more optimistic you get
# 5. The smaller the validation set, the more optimistic you get
# 6. A realistic case with some signal: non-nested vs nested cross-validation
# 7. Questions for you
#
# Requirements: `numpy`, `matplotlib`, `scikit-learn`.

# %%
import numpy as np
import matplotlib.pyplot as plt

from sklearn.svm import SVC
from sklearn.model_selection import (train_test_split, GridSearchCV,
                                     KFold, cross_val_score)
from sklearn.datasets import make_classification

rng = np.random.default_rng(42)

plt.rcParams.update({'figure.dpi': 110, 'axes.spines.top': False,
                     'axes.spines.right': False, 'font.size': 10})

# colours used throughout
VAL, TEST, OTHER = '#D85A30', '#1D9E75', '#888780'

# %% [markdown]
# ## 1. A dataset with no signal at all
#
# We generate 300 "patients" described by 20 random measurements, and give
# each of them a label (0 or 1) drawn by a coin flip, **independently** of
# the measurements. No model can do better than 50% on new patients.
#
# We split the data in three parts, as you have been told to:
# - **training** set (to fit the model),
# - **validation** set (to choose the hyperparameters),
# - **test** set (to report the final performance).
#
# Here: 150 for training, 50 for validation, 100 for testing.

# %%
def noise_dataset(n_samples=300, n_features=20, seed=0):
    r = np.random.default_rng(seed)
    X = r.normal(size=(n_samples, n_features))
    y = r.integers(0, 2, size=n_samples)  # coin flip: no relation with X
    return X, y

X, y = noise_dataset(seed=1)

X_train, X_tmp, y_train, y_tmp = train_test_split(X, y, test_size=150,
                                                  random_state=0)
X_val, X_test, y_val, y_test = train_test_split(X_tmp, y_tmp, test_size=100,
                                                random_state=0)

print('train: %i, validation: %i, test: %i' % (len(y_train), len(y_val),
                                               len(y_test)))

# %% [markdown]
# ## 2. Tuning the hyperparameters on the validation set
#
# We use a support vector machine (SVM) with a Gaussian (RBF) kernel. It has
# two hyperparameters:
# - `C`: how strongly training errors are penalised,
# - `gamma`: how "local" the decision boundary is.
#
# We try a 12 x 12 grid, i.e. **144 settings**, and record the validation
# accuracy of each one.

# %%
Cs = np.logspace(-2, 4, 12)
gammas = np.logspace(-4, 2, 12)

val_acc = np.zeros((len(Cs), len(gammas)))
test_acc = np.zeros((len(Cs), len(gammas)))  # we look at it only at the end!

for i, C in enumerate(Cs):
    for j, gamma in enumerate(gammas):
        model = SVC(C=C, gamma=gamma).fit(X_train, y_train)
        val_acc[i, j] = model.score(X_val, y_val)
        test_acc[i, j] = model.score(X_test, y_test)

i_best, j_best = np.unravel_index(np.argmax(val_acc), val_acc.shape)
print('best setting: C = %.3g, gamma = %.3g' % (Cs[i_best], gammas[j_best]))
print('validation accuracy of the best setting: %.1f%%' %
      (100 * val_acc[i_best, j_best]))

# %% [markdown]
# A validation accuracy clearly above 50%, on pure noise! Had we stopped here, we
# would have reported a "predictive model". Let's look at the test set, which
# was never used for any decision.

# %%
print('test accuracy of the same setting:       %.1f%%' %
      (100 * test_acc[i_best, j_best]))

fig, AX = plt.subplots(1, 2, figsize=(8, 3.3))
for ax, acc, title in zip(AX, [val_acc, test_acc],
                          ['validation accuracy', 'test accuracy']):
    im = ax.imshow(100 * acc, origin='lower', cmap='RdBu_r', vmin=30, vmax=70,
                   aspect='auto')
    ax.plot(j_best, i_best, 'o', mfc='none', mec='k', ms=12, mew=2)
    ax.set_xlabel('gamma index')
    ax.set_ylabel('C index')
    ax.set_title(title)
fig.colorbar(im, ax=AX, label='accuracy (%)')
AX[0].annotate('selected', (j_best, i_best), (j_best + 1.5, i_best + 1.5),
               arrowprops=dict(arrowstyle='->'))
plt.show()

# %% [markdown]
# The validation map is a patchwork of lucky and unlucky settings. The circled
# one was the luckiest on *this particular* validation set; its luck does not
# carry over to the test set.
#
# (The large uniform blocks are settings where the SVM gives up and predicts
# the same class for every patient: its accuracy is then simply the
# proportion of that class in the set.)
#
# Look at the distribution of all 144 validation scores: it is centred on
# 50%, and we picked its maximum.

# %%
fig, ax = plt.subplots(figsize=(5, 3))
ax.hist(100 * val_acc.ravel(), bins=np.arange(30, 75, 2), color=OTHER)
ax.axvline(100 * val_acc[i_best, j_best], color=VAL, lw=2,
           label='selected (validation)')
ax.axvline(100 * test_acc[i_best, j_best], color=TEST, lw=2, ls='--',
           label='selected (test)')
ax.axvline(50, color='k', lw=1, ls=':', label='chance')
ax.set_xlabel('validation accuracy (%)')
ax.set_ylabel('# settings')
ax.legend(frameon=False, fontsize=8)
plt.show()

# %% [markdown]
# ## 3. Is this just bad luck? Repeat the whole experiment
#
# One experiment proves nothing. We repeat the whole procedure (new noise
# dataset, new split, new grid search) 50 times.

# %%
def tune_on_validation(X, y, Cs, gammas, n_val=50, n_test=100, seed=0):
    """grid search on a validation set,
    returns (best validation accuracy, test accuracy of that model)"""
    X_train, X_tmp, y_train, y_tmp = train_test_split(
        X, y, test_size=n_val + n_test, random_state=seed)
    X_val, X_test, y_val, y_test = train_test_split(
        X_tmp, y_tmp, test_size=n_test, random_state=seed)
    best_val, best_model = -1, None
    for C in Cs:
        for gamma in gammas:
            model = SVC(C=C, gamma=gamma).fit(X_train, y_train)
            score = model.score(X_val, y_val)
            if score > best_val:
                best_val, best_model = score, model
    return best_val, best_model.score(X_test, y_test)

results = np.array([tune_on_validation(*noise_dataset(seed=s), Cs, gammas,
                                       seed=s) for s in range(50)])

fig, ax = plt.subplots(figsize=(3.5, 3.5))
for v, t in results:
    ax.plot([0, 1], [100 * v, 100 * t], color=OTHER, lw=0.5, alpha=0.6)
ax.plot(np.zeros(len(results)), 100 * results[:, 0], 'o', color=VAL, ms=4)
ax.plot(np.ones(len(results)), 100 * results[:, 1], 'o', color=TEST, ms=4)
ax.axhline(50, color='k', ls=':', lw=1)
ax.set_xticks([0, 1], ['best\nvalidation', 'test'])
ax.set_xlim(-0.4, 1.4)
ax.set_ylabel('accuracy (%)')
ax.set_title('50 experiments on noise')
plt.show()

print('mean best validation accuracy: %.1f%%' % (100 * results[:, 0].mean()))
print('mean test accuracy:            %.1f%%' % (100 * results[:, 1].mean()))

# %% [markdown]
# Every single experiment overestimates. This is not bad luck, it is a
# systematic **bias** created by the selection step.

# %% [markdown]
# ## 4. The more settings you try, the more optimistic you get
#
# Intuition: if you roll one die, you expect 3.5. If you roll 100 dice and
# keep the highest, you almost certainly get a 6. Trying more hyperparameter
# settings is rolling more dice.
#
# Here we evaluate the settings of the grid in a random order and track the
# best validation score found so far.

# %%
n_tries = np.array([1, 2, 5, 10, 20, 50, 100, 144])
n_rep = 30
best_val = np.zeros((n_rep, len(n_tries)))
test_of_best = np.zeros((n_rep, len(n_tries)))

grid = [(C, g) for C in Cs for g in gammas]

for rep in range(n_rep):
    X, y = noise_dataset(seed=100 + rep)
    X_train, X_tmp, y_train, y_tmp = train_test_split(X, y, test_size=150,
                                                      random_state=rep)
    X_val, X_test, y_val, y_test = train_test_split(X_tmp, y_tmp,
                                                    test_size=100,
                                                    random_state=rep)
    order = rng.permutation(len(grid))
    vals, tests = [], []
    for k in order:
        model = SVC(C=grid[k][0], gamma=grid[k][1]).fit(X_train, y_train)
        vals.append(model.score(X_val, y_val))
        tests.append(model.score(X_test, y_test))
    vals, tests = np.array(vals), np.array(tests)
    for i, n in enumerate(n_tries):
        b = np.argmax(vals[:n])
        best_val[rep, i], test_of_best[rep, i] = vals[b], tests[b]

fig, ax = plt.subplots(figsize=(4.5, 3.2))
for data, c, ls, label in [(best_val, VAL, '-', 'best validation'),
                           (test_of_best, TEST, '--', 'test of that model')]:
    m, s = 100 * data.mean(0), 100 * data.std(0) / np.sqrt(n_rep)
    ax.plot(n_tries, m, ls, marker='o', color=c, label=label)
    ax.fill_between(n_tries, m - s, m + s, color=c, alpha=0.2, lw=0)
ax.axhline(50, color='k', ls=':', lw=1)
ax.set_xscale('log')
ax.set_xlabel('# hyperparameter settings tried')
ax.set_ylabel('accuracy (%)')
ax.legend(frameon=False, fontsize=8)
plt.show()

# %% [markdown]
# The test accuracy stays at chance whatever we do; only our *illusion* of
# performance grows with the size of the search.

# %% [markdown]
# ## 5. The smaller the validation set, the more optimistic you get
#
# With a small validation set, each score is very noisy (with 50 patients,
# a single patient is worth 2%), so the luckiest setting is luckier.

# %%
val_sizes = [25, 50, 100, 200, 400]
gaps = []
for n_val in val_sizes:
    g = []
    for s in range(15):
        X, y = noise_dataset(n_samples=150 + n_val + 100, seed=1000 + s)
        v, t = tune_on_validation(X, y, Cs[::2], gammas[::2], n_val=n_val,
                                  seed=s)
        g.append(v - t)
    gaps.append(g)
gaps = 100 * np.array(gaps)

fig, ax = plt.subplots(figsize=(4.5, 3.2))
ax.errorbar(val_sizes, gaps.mean(1), gaps.std(1) / np.sqrt(gaps.shape[1]),
            marker='o', color=VAL, capsize=3)
ax.axhline(0, color='k', ls=':', lw=1)
ax.set_xscale('log')
ax.set_xticks(val_sizes, val_sizes)
ax.set_xlabel('validation set size')
ax.set_ylabel('optimism (validation - test, %)')
plt.show()

# %% [markdown]
# ## 6. A realistic case: non-nested vs nested cross-validation
#
# Real datasets usually contain *some* signal, and with few patients we
# rarely afford a separate test set. A very common practice is:
#
# ```python
# search = GridSearchCV(model, param_grid, cv=5).fit(X, y)
# print(search.best_score_)   # <- reported as "the" performance
# ```
#
# `best_score_` is the best of many cross-validated scores: the same winner's
# curse as above. The fix is **nested cross-validation**: an *inner* loop
# chooses the hyperparameters, an *outer* loop evaluates the whole procedure
# (tuning included) on data that the inner loop never saw.
#
# ```
# outer fold 1:  [ inner CV -> choose C, gamma ]  -> score on held-out fold 1
# outer fold 2:  [ inner CV -> choose C, gamma ]  -> score on held-out fold 2
# ...
# ```
#
# To know the *true* accuracy, we cheat in a way only simulations allow: for
# each small dataset of 60 patients, we also generate 5000 new patients
# from the same distribution.

# %%
param_grid = {'C': np.logspace(-2, 4, 12), 'gamma': np.logspace(-4, 1, 12)}

def one_realistic_experiment(seed, n_samples=60):
    X_all, y_all = make_classification(
        n_samples=n_samples + 5000, n_features=20, n_informative=3,
        n_redundant=0, flip_y=0.3, class_sep=0.8, random_state=seed)
    X, y = X_all[:n_samples], y_all[:n_samples]
    X_new, y_new = X_all[n_samples:], y_all[n_samples:]

    inner = KFold(5, shuffle=True, random_state=seed)
    outer = KFold(5, shuffle=True, random_state=seed + 1)
    search = GridSearchCV(SVC(), param_grid, cv=inner)

    non_nested = search.fit(X, y).best_score_
    nested = cross_val_score(search, X, y, cv=outer).mean()
    true = search.best_estimator_.score(X_new, y_new)
    return non_nested, nested, true

res = np.array([one_realistic_experiment(seed) for seed in range(20)])
res = 100 * res

fig, ax = plt.subplots(figsize=(4.5, 3.5))
labels = ['non-nested CV\n(best_score_)', 'nested CV', 'true accuracy\n(5000 new patients)']
for k, (c, lab) in enumerate(zip([VAL, '#534AB7', TEST], labels)):
    ax.plot(k + 0.08 * rng.normal(size=len(res)), res[:, k], 'o', color=c,
            ms=4, alpha=0.7)
    ax.plot([k - 0.25, k + 0.25], [res[:, k].mean()] * 2, color=c, lw=3)
ax.set_xticks(range(3), labels, fontsize=8)
ax.set_ylabel('accuracy (%)')
ax.set_title('20 small datasets with a weak signal')
plt.show()

print('mean non-nested estimate: %.1f%%' % res[:, 0].mean())
print('mean nested estimate:     %.1f%%' % res[:, 1].mean())
print('mean true accuracy:       %.1f%%' % res[:, 2].mean())

# %% [markdown]
# The non-nested estimate is systematically too high. The nested estimate is
# close to the truth on average, and if anything slightly pessimistic: each
# outer model is trained on only 80% of the patients. It is still noisy for
# any single dataset (60 patients is not much), but an honest error is much
# better than a systematic one.
#
# (This section takes a couple of minutes to run: 20 datasets x 6 grid
# searches x 144 settings x 5 folds.)
#
# ### Take-home messages
#
# - Every decision taken by looking at a score "uses up" that data: the score
#   becomes optimistic.
# - The bias grows with the number of settings tried and shrinks with the
#   size of the validation set.
# - Keep a test set that is used **once**, at the very end. With few data,
#   use nested cross-validation.
# - The same trap appears in disguise: choosing the features, the
#   preprocessing, the architecture, the random seed, or even stopping the
#   project "when the result looks good" are all hyperparameter choices.

# %% [markdown]
# ## 7. Questions for you
#
# 1. In section 2, replace the 12 x 12 grid by a 3 x 3 grid. What happens to
#    the best validation accuracy? Explain.
# 2. A colleague tries 1000 random seeds for the weight initialisation of a
#    neural network and reports the best validation accuracy. What is wrong?
#    How would you fix it?
# 3. In section 6, a student first selects the 3 features most correlated
#    with the label *on the whole dataset*, then runs nested cross-validation
#    on those 3 features. Is the nested estimate still honest? Try it
#    (hint: use the pure-noise dataset of section 1).
# 4. After looking at the test score, you are disappointed and change the
#    model. What has just happened to your test set?
