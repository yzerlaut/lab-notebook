# %% [markdown]
# # Project 4: A clinical score calculator
#
# **Clinical question:** can we compute validated clinical scores reliably
# for a whole ward of patients, and catch impossible or missing data?
#
# **What you will build:**
# 1. Functions computing the CHA₂DS₂-VASc, qSOFA and Glasgow Coma Scale scores
# 2. Input validation (impossible values, missing data)
# 3. Tests to make sure your functions are correct
# 4. Batch scoring of a table of patients, with a summary figure
# 5. (Optional) A small interactive calculator
#
# Cells marked **TODO** are for you to complete.
#
# ⚠️ This is a teaching exercise. Always check the official definition of a
# score before using it clinically.

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %% [markdown]
# ## 1. CHA₂DS₂-VASc (stroke risk in atrial fibrillation)
#
# | Item | Points |
# |---|---|
# | Congestive heart failure | 1 |
# | Hypertension | 1 |
# | Age ≥ 75 | 2 |
# | Diabetes | 1 |
# | Prior stroke / TIA / thromboembolism | 2 |
# | Vascular disease (MI, peripheral artery disease, aortic plaque) | 1 |
# | Age 65 to 74 | 1 |
# | Sex category: female | 1 |

# %%
def cha2ds2_vasc(age, sex, heart_failure, hypertension, diabetes,
                 stroke_history, vascular_disease):
    score = 0
    if heart_failure:
        score += 1
    if hypertension:
        score += 1
    if age >= 75:
        score += 2
    elif age >= 65:
        score += 1
    if diabetes:
        score += 1
    if stroke_history:
        score += 2
    if vascular_disease:
        score += 1
    if sex == 'F':
        score += 1
    return score

cha2ds2_vasc(age=78, sex='F', heart_failure=False, hypertension=True,
             diabetes=False, stroke_history=False, vascular_disease=False)

# %% [markdown]
# ## 2. qSOFA (sepsis screening)
#
# One point each for: respiratory rate ≥ 22/min, altered mentation
# (Glasgow < 15), systolic blood pressure ≤ 100 mmHg.
# A score ≥ 2 suggests a high risk of poor outcome.
#
# **TODO:** complete the function.

# %%
def qsofa(respiratory_rate, systolic_bp, glasgow):
    score = 0
    # TODO
    return score

# %% [markdown]
# ## 3. Glasgow Coma Scale
#
# Eyes (1 to 4) + Verbal (1 to 5) + Motor (1 to 6), total from 3 to 15.
#
# **TODO:** complete the function, and make it refuse impossible values
# by raising an error: `raise ValueError('verbal must be between 1 and 5')`.

# %%
def glasgow(eyes, verbal, motor):
    # TODO: validate each component
    return eyes + verbal + motor

# %% [markdown]
# ## 4. Validating the inputs
#
# A score computed from wrong data is worse than no score at all.
#
# **TODO:** add validation to `cha2ds2_vasc` and `qsofa`:
# - age must be between 0 and 120
# - sex must be `'M'` or `'F'`
# - respiratory rate between 0 and 80, systolic pressure between 30 and 300
# - missing values (`None` or `np.nan`) must raise an error, not be silently
#   treated as "no"

# %%
def check_range(value, name, low, high):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        raise ValueError(f'{name} is missing')
    if not (low <= value <= high):
        raise ValueError(f'{name}={value} is outside [{low}, {high}]')

# %% [markdown]
# ## 5. Test your functions
#
# Professional software is tested. Each `assert` checks a case where we know
# the right answer; it raises an error if the function is wrong.
#
# **TODO:** add at least three tests per score, including edge cases
# (age exactly 65, exactly 75, respiratory rate exactly 22...).

# %%
assert cha2ds2_vasc(50, 'M', False, False, False, False, False) == 0
assert cha2ds2_vasc(78, 'F', False, True, False, False, False) == 4
assert cha2ds2_vasc(65, 'M', False, False, False, False, False) == 1
# TODO: qsofa tests, glasgow tests
print('All tests passed')

# %% [markdown]
# ## 6. Scoring a whole ward
#
# We generate a table of fictitious patients. In real life, this would come
# from a CSV export (`pd.read_csv`).

# %%
rng = np.random.default_rng(1)
n = 200
ward = pd.DataFrame({
    'age': rng.integers(40, 95, n),
    'sex': rng.choice(['M', 'F'], n),
    'heart_failure': rng.random(n) < 0.2,
    'hypertension': rng.random(n) < 0.5,
    'diabetes': rng.random(n) < 0.25,
    'stroke_history': rng.random(n) < 0.1,
    'vascular_disease': rng.random(n) < 0.15,
    'respiratory_rate': rng.normal(18, 5, n).round(),
    'systolic_bp': rng.normal(125, 25, n).round(),
    'glasgow': np.clip(15 - rng.poisson(0.4, n), 3, 15),
})
# introduce a few data entry errors, as in real life
ward.loc[3, 'age'] = 250
ward.loc[17, 'systolic_bp'] = np.nan
ward.head()

# %%
def score_patient(row):
    try:
        cha = cha2ds2_vasc(row['age'], row['sex'], row['heart_failure'],
                           row['hypertension'], row['diabetes'],
                           row['stroke_history'], row['vascular_disease'])
        q = qsofa(row['respiratory_rate'], row['systolic_bp'], row['glasgow'])
        return pd.Series({'CHA2DS2-VASc': cha, 'qSOFA': q, 'error': ''})
    except ValueError as e:
        return pd.Series({'CHA2DS2-VASc': np.nan, 'qSOFA': np.nan, 'error': str(e)})

scores = ward.apply(score_patient, axis=1)
ward = pd.concat([ward, scores], axis=1)

print('Patients with invalid data:')
ward[ward['error'] != '']

# %% [markdown]
# **TODO:**
# - Plot the distribution of CHA₂DS₂-VASc scores (bar plot).
# - Current guidelines recommend anticoagulation from a score of 2 in men
#   and 3 in women. How many patients of the ward are concerned?
# - List the patients with qSOFA ≥ 2, sorted by score: this is your
#   "patients to see first" list.

# %%
# TODO

# %% [markdown]
# ## 7. (Optional) An interactive calculator
#
# **TODO:** Write a function `ask_patient()` that asks the questions with
# `input()`, re-asks when the answer is invalid, and prints all the scores.
#
# **Questions for your report:**
# - Which errors did your validation catch? Which ones could it never catch?
# - Why do scores use simple integer points rather than a precise formula?
