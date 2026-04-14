# %%
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder,\
      OneHotEncoder, OrdinalEncoder, PolynomialFeatures

from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA

import seaborn as sns
import matplotlib.pylab as plt

import warnings
warnings.filterwarnings('ignore')


# %%
X_train = pd.read_csv('X_train.csv')
y_train = pd.read_csv('y_train.csv')
X_test = pd.read_csv('X_test.csv')
test_ids = X_test['patient_id']

print(f'Train : {X_train.shape[0]} patients, {X_train.shape[1]} variables')
print(f'Test  : {X_test.shape[0]} patients')
print(f'\nClasses ({y_train["sfdm2"].nunique()}) :')
print(y_train['sfdm2'].value_counts())

cat_cols = [c for c in X_train.select_dtypes(include='object').columns.tolist()\
                     if c!= 'patient_id']
num_cols = X_train.select_dtypes(include='number').columns.tolist()
print(f'Variables catégorielles ({len(cat_cols)}) : {cat_cols}')
print(f'Variables numériques ({len(num_cols)}) : {num_cols}')

# %%
df = pd.DataFrame(X_train)
df.drop('patient_id', axis=1)
df['target'] = y_train['sfdm2']

for col in num_cols:
    fig, ax = plt.subplots()
    sns.histplot(data=df, x=col, hue='target', ax=ax)
    # ax.legend(frameon=False)

# %%

# # %% [markdown]
# for now, I drop 
# - `dnr` with values: ['dnr after sadm', 'no dnr', 'dnr before sadm'

income_order = [ "under $11k", "$11-$25k", "$25-$50k", ">$50k" ]

log_transformer = FunctionTransformer(np.log1p, 
                                      feature_names_out="one-to-one")

# for those columns, we have a specific value to Impute
CONST_Imputer_Columns = \
    ["alb", "pafi", "bili", "crea", "bun", "wblc", "urine"]

NOMINAL_COLUMNS = [c for c in cat_cols\
                    if c not in ['income', 'dzclass', 'race']]

# num_preprocessing = ColumnTransformer(transformers=[
#     # IMPUTE VALUES
#     ("impute_alb", SimpleImputer(strategy="constant", fill_value=3.5), ["alb"]),
#     ("impute_pafi", SimpleImputer(strategy="constant", fill_value=333.3), ["pafi"]),
#     ("impute_bili", SimpleImputer(strategy="constant", fill_value=1.01), ["bili"]),
#     ("impute_crea", SimpleImputer(strategy="constant", fill_value=1.01), ["crea"]),
#     ("impute_bun", SimpleImputer(strategy="constant", fill_value=6.51), ["bun"]),
#     ("impute_wblc", SimpleImputer(strategy="constant", fill_value=9.0), ["wblc"]),
#     ("impute_urine", SimpleImputer(strategy="constant", fill_value=2502), ["urine"]),
#     # median for the rest of numerical values
#     ("impute_median", SimpleImputer(strategy="median"),
#                 [col for col in num_cols if col not in CONST_Imputer_Columns]),
#     # LOG some features
#     ("logs", log_transformer, ["bun", "crea", "alb", "wblc", "scoma"]),
# ], remainder="drop")   # "passthrough" keeps other columns as-is

# WBLC
wblc_proc = Pipeline(steps=[
    ("impute", SimpleImputer(strategy="constant", fill_value=9.0)),
    # ("logs", log_transformer),
    # ("poly", PolynomialFeatures(degree=2, include_bias=False)),
])

preprocessor = ColumnTransformer(transformers=[
    # DROP COLUMNS
    # ("drop_columns", "drop", ['patient_id', 'dnr', 'dzclass', 'dzgroup']),
    # IMPUTE VALUES
    ("impute_alb", SimpleImputer(strategy="constant", fill_value=3.5), ["alb"]),
    ("impute_pafi", SimpleImputer(strategy="constant", fill_value=333.3), ["pafi"]),
    ("impute_bili", SimpleImputer(strategy="constant", fill_value=1.01), ["bili"]),
    ("impute_crea", SimpleImputer(strategy="constant", fill_value=1.01), ["crea"]),
    ("impute_bun", SimpleImputer(strategy="constant", fill_value=6.51), ["bun"]),
    ("impute_urine", SimpleImputer(strategy="constant", fill_value=2502), ["urine"]),
    # median for the rest of numerical values
    ("impute_median", SimpleImputer(strategy="median"),
                [col for col in num_cols if col not in CONST_Imputer_Columns]),
    # log
    # ("logs", log_transformer, ["bun", "crea", "bili", "alb", "wblc", "scoma"]),
    ("logs", log_transformer, ["bun", "crea", "alb", "wblc", "scoma"]),
    # ("procw", wblc_proc, ['wblc']),
    # ("poly", PolynomialFeatures(degree=2), ['wblc']),
    # ENCODE ORDINAL VALUES
    # ("income_ord", OrdinalEncoder(categories=[income_order],
    #                     handle_unknown="use_encoded_value",
    #                     unknown_value=-1, encoded_missing_value=-1), ["income"]),
    # ENCODE NOMINAL VALUES
    ("encode_nominal", OneHotEncoder(sparse_output=False, 
                                     drop='first',
                                     handle_unknown='ignore'), NOMINAL_COLUMNS),
    # ("drop", "drop", "encode_nominal__dnr_nan"),
    # ("drop_columns", "drop", ['impute_median__scoma']),
], remainder="drop")   # "passthrough" keeps other columns as-is

pca = PCA(n_components=10)

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("impute", SimpleImputer(strategy='most_frequent')),
    ("scaler", StandardScaler()),
    # ("pca", pca),
])
X_train_scaled = pipeline.fit_transform(X_train, y_train)

new_features = pipeline.named_steps['preprocessor'].get_feature_names_out()

# df = pd.DataFrame()
# df['target'] = y_train['sfdm2']
# for i, col in enumerate(new_features):
#     df[col] = X_train_scaled[:,i]
#     fig, ax = plt.subplots()
#     sns.histplot(data=df, x=col, hue='target', ax=ax)
# # %%

pipe= Pipeline(steps=[
    ("model", LogisticRegression(max_iter=4000,
                                 class_weight='balanced')),
])
X_train_scaled = pipeline.fit_transform(X_train, y_train)

pipe.fit(X_train_scaled, y_train['sfdm2'])

new_features = pipeline.named_steps['preprocessor'].get_feature_names_out()
print(new_features)
print(len(new_features))
print(f'Train : {X_train_scaled.shape[0]} patients, {X_train_scaled.shape[1]} variables')

# Hyperparameters
param_grid = {
    "model__C": np.logspace(-2, 2, 30),
}
from sklearn.model_selection import GridSearchCV
# CV Search
grid = GridSearchCV(
    estimator=pipe,
    param_grid={"model__C":np.logspace(-8, -1, 200)},
    cv=5,
    scoring="f1_macro",
    n_jobs=-1
)
grid.fit(X_train_scaled, y_train['sfdm2'])

print("Best params:", grid.best_params_)
print("Best CV score:", grid.best_score_)

# %%
# model = LogisticRegression(max_iter=2000, 
#                            random_state=12, 
#                            C=1e-2,
#                            class_weight='balanced')
model = RandomForestClassifier(max_depth=5)
model.fit(X_train_scaled, y_train['sfdm2'])

# Validation croisée sur le train (F1-macro)
scores = cross_val_score(model, X_train_scaled, y_train['sfdm2'], 
                         cv=5, scoring='f1_macro')
print(f'F1-macro en validation croisée : {scores.mean():.3f} (+/- {scores.std():.3f})')

# %%
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV, StratifiedKFold
from scipy.stats import uniform, randint
param_dist = {
    "n_estimators":      randint(100, 800),
    "max_depth":         [None, 5, 10, 20],
    "min_samples_split": randint(2, 20),
    "min_samples_leaf":  randint(1, 10),
    "max_features":      ["sqrt", "log2", 0.3, 0.5, None],
    "max_samples":       uniform(0.6, 0.4),      # bagging fraction
    "class_weight":      ["balanced", "balanced_subsample", None],
    "criterion":         ["gini", "entropy"],
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=12)

random_search = RandomizedSearchCV(
    estimator=RandomForestClassifier(random_state=12, n_jobs=-1),
    param_distributions=param_dist,
    n_iter=100,             # number of random combinations to try
    scoring="f1_macro",     # good for 4-class; alternatives: "balanced_accuracy", "roc_auc_ovr"
    cv=cv,
    verbose=2,
    random_state=42,
    n_jobs=-1,
    return_train_score=True,
)

random_search.fit(X_train_scaled, y_train['sfdm2'])

print("Best params:", random_search.best_params_)
print("Best CV score:", random_search.best_score_)


# %%
X_test_scaled = pipeline.transform(X_test)
y_pred = random_search.predict(X_test_scaled)

submission = pd.DataFrame({
    'patient_id': test_ids,
    'sfdm2': y_pred
})
submission.to_csv('submission.csv', index=False)
print(f'Soumission sauvegardée : {len(submission)} prédictions')
print(f'\nDistribution des prédictions :')
print(submission['sfdm2'].value_counts())
print(f'\nAperçu :')
submission.head()
# -

# %%
X_test_scaled = pipeline.transform(X_test)


# %%
# pipeline.fit(X_train)
# X_train = pipeline.fit_transform(X_train, y_train)
X_train_scaled = pipeline.fit_transform(X_train, y_train)
print(f'Train : {nX_train.shape[0]} patients, {nX_train.shape[1]} variables')
# X_train[num_cols].isna().sum(axis=1)
# np.isnan(np.array(X_train)).sum(axis=1)

# %%

df = pd.DataFrame(X_train)
df['target'] = y_train['sfdm2']

import seaborn as sns
sns.histplot(df, x='age', hue='target')


# %%
# ### 5.2 Prétraitement

# %%
# Sauvegarder les patient_id du test pour la soumission
test_ids = X_test['patient_id'].copy()

# Supprimer patient_id (ce n'est pas une variable prédictive)
X_train = X_train.drop(columns=['patient_id'])
X_test = X_test.drop(columns=['patient_id'])
target = y_train['sfdm2']

# Identifier les colonnes catégorielles et numériques
cat_cols = X_train.select_dtypes(include='object').columns.tolist()
num_cols = X_train.select_dtypes(include='number').columns.tolist()
print(f'Variables catégorielles ({len(cat_cols)}) : {cat_cols}')
print(f'Variables numériques ({len(num_cols)}) : {num_cols}')

# %%
# Encoder les variables catégorielles
encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    combined = pd.concat([X_train[col], X_test[col]]).astype(str)
    le.fit(combined)
    X_train[col] = le.transform(X_train[col].astype(str))
    X_test[col] = le.transform(X_test[col].astype(str))
    encoders[col] = le

# Imputer les valeurs manquantes par la médiane (calculée sur le train)
medians = X_train.median()
X_train = X_train.fillna(medians)
X_test = X_test.fillna(medians)

# Standardiser
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
# -

# ### 5.3 Entraînement et évaluation

# %%
model = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
model.fit(X_train_scaled, target)

# Validation croisée sur le train (F1-macro)
scores = cross_val_score(model, X_train_scaled, target, cv=5, scoring='f1_macro')
print(f'F1-macro en validation croisée : {scores.mean():.3f} (+/- {scores.std():.3f})')
# -

# ### 5.4 Générer la soumission

# %%
X_test_scaled = pipeline.fit_transform(X_test)
y_pred = grid.predict(X_test_scaled)

submission = pd.DataFrame({
    'patient_id': test_ids,
    'sfdm2': y_pred
})
submission.to_csv('submission.csv', index=False)
print(f'Soumission sauvegardée : {len(submission)} prédictions')
print(f'\nDistribution des prédictions :')
print(submission['sfdm2'].value_counts())
print(f'\nAperçu :')
submission.head()
# %%

df['target'] = (y_train['sfdm2']=='dead')

# %%

# %%
df['income'].unique()
df['income-num'] = np.nan+0*df['age']
# print(df['income-num'])
for i, inc in enumerate(['under $11k', '$25-$50k', '$11-$25k', '>$50k']):
    cond = (df['income']==inc)
    df['income-num'][cond] = i

# %%
fig, ax = plt.subplots()
sns.histplot(data=df, x='edu', hue='income')
# ax.scatter(df['income-num'], df['edu'])

# %%
df = pd.DataFrame(X_train)
df['target'] = y_train['sfdm2']
# %%
sns.histplot(data=df, x='scoma', hue='target')

# %%
df['log-scoma'] = np.log1p(df['scoma'])
sns.histplot(data=df, x='log-scoma', hue='target')

# %%
sns.heatmap(df[['age', 'avtisst', 'log-scoma', 'target']].corr(),
            cmap='coolwarm', center=0, fmt='.2f', annot=True)
# %%
