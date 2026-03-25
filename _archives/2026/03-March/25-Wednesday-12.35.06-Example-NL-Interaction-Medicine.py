# %% [markdown]
# # Example of Non-Linear Interaction between Features in Medicine 
# 
# From the paper:
# https://doi.org/10.1186/s12911-020-1023-5 
# *Machine learning can predict survival of patients with heart failure from serum creatinine and ejection fraction alone*
# 
# link to dataset: https://archive.ics.uci.edu/dataset/519/heart+failure+clinical+records
# 
# 
# The interaction between ejection fraction (how much blood the heart pumps per beat) and serum creatinine (kidney function) is non-linearly related to the death prodiction.
#
# Neither feature alone predicts death reliably, but low ejection fraction combined with high creatinine creates a cardiorenal syndrome with dramatically worse prognosis. 
# 
# This is a multiplicative, threshold-gated effect logistic regression cannot capture. 
#
# N.B. Age further modulates this interaction non-linearly.
#

# %%
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns

# %%
# fetch dataset 
from ucimlrepo import fetch_ucirepo
heart_failure_clinical_records = fetch_ucirepo(id=519) 
  
# data (as pandas dataframes) 
X = heart_failure_clinical_records.data.features 
y = heart_failure_clinical_records.data.targets 
X['target'] = y

# for plotting, we limit the range of shown values
ef_range = [10, 60]
sc_range = [0.5, 6.0]

# %%
fig, AX = plt.subplots(1, 5, figsize=(10,1.3))
plt.subplots_adjust(wspace=0.7)

sns.histplot(data=X, 
     x='ejection_fraction',
     hue='target',
     kde=True, # kernel density
    #  bins=40,
     ax=AX[0])

sns.histplot(data=X, 
     x='serum_creatinine',
     hue='target',
     kde=True, # kernel density
    #  bins=40,
     ax=AX[1])

sns.scatterplot(data=X,
                x='ejection_fraction',
                y='serum_creatinine',
                hue='target',
                alpha=.3,
                ax=AX[2])

sns.kdeplot(data=X,
                x='ejection_fraction',
                y='serum_creatinine',
                hue='target',
                levels=10, 
                threshold=.95,
                ax=AX[3])
# AX[3].set_xlim([10, 60])
# # pt.set_plot(AX[2], xlim=[10,60], ylim=[.5,6])
# AX[3].legend(loc=(0.,1))

for ax in AX[2:]:
    ax.set_xlim(ef_range)
    ax.set_ylim(sc_range)
AX[1].set_ylim(sc_range)
for ax in AX:
    try:
        ax.get_legend().remove()
    except AttributeError:
        pass

# 
#  
# metadata 
# print(heart_failure_clinical_records.metadata) 
  
# variable information 
# print(heart_failure_clinical_records.variables)
X
from sklearn.preprocessing import StandardScaler
# %%
fig, ax = pt.figure()
scaler = StandardScaler()
col = 'ejection_fraction'
scaler.fit(X.loc[:,X.columns==col])
x1 = scaler.transform(X.loc[:,X.columns==col].values)
ax.scatter(x1, y, alpha=.2)
# ax.scatter(X['creatinine_phosphokinase'], y, alpha=.2)
# %%
fig, ax = pt.figure()
col = 'serum_creatinine'
scaler.fit(X.loc[:,X.columns==col])
x2 = scaler.transform(X.loc[:,X.columns==col].values)
ax.scatter(x2, y, alpha=.2)
# ax.scatter(X['serum_creatinine'], y, alpha=.2)

# %%
fig, ax = pt.figure()
ax.scatter(x1**1*x2**2, y, alpha=.2)

# %%
import seaborn as sns
# sns.set_theme(font_size=2)

# make histogram
# col = 'ejection_fraction'
col = 'serum_creatinine'
ax = sns.histplot(data=X, 
     x=col,
     hue='target',
     kde=True, # kernel density
     bins=40)
# pt.plt.xlim([0,5.])


# %%
X['merged'] = x1**2*x2**2
X['merged'][X['merged']>2] = 2
ax = sns.histplot(data=X, 
     x='merged',
     hue='target',
     kde=True, # kernel density
     bins=np.linspace(0.05,1,20))
ax.set_xscale('log')
# ax.set_yscale('log')
ax.set_xlim([0.05,2])
# %%
