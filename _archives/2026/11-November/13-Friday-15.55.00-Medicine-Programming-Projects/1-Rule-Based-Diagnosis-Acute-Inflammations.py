# %% [markdown]
# # Project 1: A rule-based diagnostic system (in the spirit of MYCIN)
#
# **Clinical question:** from six simple clinical signs, can we diagnose
# *inflammation of the urinary bladder* and *nephritis of renal pelvis origin*?
#
# **Dataset:** UCI "Acute Inflammations" (Czerniak & Zarzycki, 2003),
# 120 patients, 6 attributes, 2 binary diagnoses.
#
# **What you will build:**
# 1. Hand-written diagnostic rules (`if ... and ...:`)
# 2. An interactive consultation that asks the patient questions
# 3. Certainty factors to combine evidence, as in MYCIN
# 4. An evaluation of your rules on the full dataset (sensitivity, specificity)
# 5. (Optional) A decision tree learnt from the data, compared with your rules
#
# Cells marked **TODO** are for you to complete.

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %% [markdown]
# ## 1. Load the dataset
#
# Download `acute+inflammations.zip` from
# https://archive.ics.uci.edu/dataset/184/acute+inflammations
# and put `diagnosis.data` next to this notebook.
# The file is a bit unusual: UTF-16 encoded, tab-separated, with a comma as
# decimal separator (37,9 instead of 37.9).

# %%
columns = ['temperature', 'nausea', 'lumbar_pain', 'urine_pushing',
           'micturition_pain', 'urethra_burning',
           'bladder_inflammation', 'nephritis']

def load_acute_inflammations(filename='diagnosis.data'):
    df = pd.read_csv(filename, sep='\t', header=None, names=columns,
                     encoding='utf-16', decimal=',')
    # convert "yes"/"no" strings into True/False
    for c in columns[1:]:
        df[c] = df[c].str.strip() == 'yes'
    return df

try:
    df = load_acute_inflammations()
except FileNotFoundError:
    # alternative: pip install ucimlrepo
    from ucimlrepo import fetch_ucirepo
    data = fetch_ucirepo(id=184)
    df = pd.concat([data.data.features, data.data.targets], axis=1)
    df.columns = columns
    df['temperature'] = df['temperature'].astype(str).str.replace(',', '.').astype(float)
    for c in columns[1:]:
        df[c] = df[c].astype(str).str.strip() == 'yes'

df.head()

# %% [markdown]
# ## 2. Explore the data
#
# **TODO:** How many patients have each diagnosis? Both? Neither?
# Plot the temperature distribution for patients with and without nephritis.

# %%
print('Number of patients:', len(df))
print('Bladder inflammation:', df['bladder_inflammation'].sum())
print('Nephritis:', df['nephritis'].sum())
# TODO: count patients with both diagnoses, and with none

fig, ax = plt.subplots(figsize=(5, 3))
ax.hist(df.loc[~df['nephritis'], 'temperature'], bins=15, alpha=0.6, label='no nephritis')
ax.hist(df.loc[df['nephritis'], 'temperature'], bins=15, alpha=0.6, label='nephritis')
ax.set_xlabel('temperature (°C)')
ax.set_ylabel('patients')
ax.legend()

# %% [markdown]
# **TODO:** For each symptom, compute the fraction of patients that show it,
# separately for each diagnosis. Which symptoms seem most informative?

# %%
symptoms = columns[1:6]
df.groupby('nephritis')[symptoms].mean()

# %% [markdown]
# ## 3. Hand-written rules
#
# A patient is represented as a dictionary, for example:

# %%
example_patient = {'temperature': 40.2, 'nausea': True, 'lumbar_pain': True,
                   'urine_pushing': False, 'micturition_pain': False,
                   'urethra_burning': False}

# %% [markdown]
# **TODO:** Write your own rules from your medical knowledge and from the
# exploration above. Each function returns `True` or `False`.

# %%
def has_fever(patient):
    return patient['temperature'] >= 38.0

def rule_nephritis(patient):
    # TODO: improve this rule
    if has_fever(patient) and patient['lumbar_pain']:
        return True
    return False

def rule_bladder_inflammation(patient):
    # TODO: improve this rule
    if patient['urine_pushing'] and patient['micturition_pain']:
        return True
    return False

print('Nephritis?', rule_nephritis(example_patient))
print('Bladder inflammation?', rule_bladder_inflammation(example_patient))

# %% [markdown]
# ## 4. An interactive consultation
#
# MYCIN worked as a dialogue: it asked the physician questions one by one.
# Run the cell below and answer the questions.

# %%
def ask_yes_no(question):
    answer = ''
    while answer not in ['y', 'n']:
        answer = input(question + ' (y/n) ').strip().lower()
    return answer == 'y'

def consultation():
    patient = {}
    patient['temperature'] = float(input('Body temperature (°C)? '))
    patient['nausea'] = ask_yes_no('Nausea?')
    patient['lumbar_pain'] = ask_yes_no('Lumbar pain?')
    patient['urine_pushing'] = ask_yes_no('Urine pushing (continuous need to urinate)?')
    patient['micturition_pain'] = ask_yes_no('Pain on micturition?')
    patient['urethra_burning'] = ask_yes_no('Burning of urethra, itch, swelling of urethra outlet?')

    print('\n--- Conclusion ---')
    if rule_nephritis(patient):
        print('Suspected nephritis of renal pelvis origin')
    if rule_bladder_inflammation(patient):
        print('Suspected inflammation of the urinary bladder')
    if not rule_nephritis(patient) and not rule_bladder_inflammation(patient):
        print('No diagnosis suggested by the rules')
    return patient

# uncomment to run the consultation
# patient = consultation()

# %% [markdown]
# **TODO:** Make the consultation smarter: skip questions whose answer cannot
# change the conclusion anymore (this is what MYCIN's goal-driven,
# "backward chaining" reasoning did).

# %% [markdown]
# ## 5. Certainty factors
#
# Real symptoms are rarely conclusive. In MYCIN, each rule brings a
# *certainty factor* (CF) between 0 and 1 in favour of a diagnosis.
# Two positive pieces of evidence are combined as:
#
# $$ CF = CF_1 + CF_2 \, (1 - CF_1) $$
#
# so that evidence accumulates but never exceeds 1.

# %%
def combine_cf(cf1, cf2):
    return cf1 + cf2 * (1 - cf1)

# Each rule: (diagnosis, condition function, certainty factor)
# TODO: add your own rules and tune the CF values
rules = [
    ('nephritis', lambda p: has_fever(p), 0.4),
    ('nephritis', lambda p: p['lumbar_pain'], 0.5),
    ('nephritis', lambda p: p['nausea'], 0.2),
    ('bladder_inflammation', lambda p: p['urine_pushing'], 0.5),
    ('bladder_inflammation', lambda p: p['micturition_pain'], 0.4),
    ('bladder_inflammation', lambda p: p['urethra_burning'], 0.2),
]

def infer(patient, rules):
    certainty = {'nephritis': 0.0, 'bladder_inflammation': 0.0}
    for diagnosis, condition, cf in rules:
        if condition(patient):
            certainty[diagnosis] = combine_cf(certainty[diagnosis], cf)
    return certainty

infer(example_patient, rules)

# %% [markdown]
# **TODO:** Add *negative* evidence (a CF between -1 and 0, e.g. "absence of
# lumbar pain argues against nephritis"). Look up the full MYCIN combination
# formula for mixed positive and negative CFs and implement it.

# %% [markdown]
# ## 6. Evaluate your system on the 120 patients
#
# We call a diagnosis positive when its certainty exceeds a threshold.

# %%
def evaluate(df, rules, diagnosis, threshold=0.5):
    predictions = []
    for _, row in df.iterrows():
        certainty = infer(row.to_dict(), rules)
        predictions.append(certainty[diagnosis] >= threshold)
    predictions = np.array(predictions)
    truth = df[diagnosis].values

    TP = np.sum(predictions & truth)
    TN = np.sum(~predictions & ~truth)
    FP = np.sum(predictions & ~truth)
    FN = np.sum(~predictions & truth)
    return {'sensitivity': TP / (TP + FN),
            'specificity': TN / (TN + FP),
            'confusion': np.array([[TN, FP], [FN, TP]])}

for diagnosis in ['nephritis', 'bladder_inflammation']:
    result = evaluate(df, rules, diagnosis)
    print(f"{diagnosis}: sensitivity={result['sensitivity']:.2f}, "
          f"specificity={result['specificity']:.2f}")
    print(result['confusion'])

# %% [markdown]
# **TODO:** Vary the threshold from 0 to 1 and plot sensitivity against
# 1 - specificity (a ROC curve). Which threshold would you choose in a
# clinical setting, and why?

# %%
# TODO

# %% [markdown]
# ## 7. (Optional) Let the computer learn the rules
#
# A decision tree learns `if/else` rules directly from the data.
# Compare the learnt rules with yours.

# %%
from sklearn.tree import DecisionTreeClassifier, export_text

X = df[columns[:6]].astype(float)
for diagnosis in ['nephritis', 'bladder_inflammation']:
    tree = DecisionTreeClassifier(max_depth=3).fit(X, df[diagnosis])
    print(f'--- {diagnosis} ---')
    print(export_text(tree, feature_names=columns[:6]))

# %% [markdown]
# **Questions for your report:**
# - Are the learnt rules similar to yours? Are they medically sensible?
# - The tree is evaluated on the data it was trained on. Why is that a problem?
#   (Hint: look up `train_test_split`.)
# - What are the advantages of a rule-based system over a learnt model for a
#   physician? And the drawbacks?
