# %%
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder,\
      OneHotEncoder, OrdinalEncoder, PolynomialFeatures

from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline, FunctionTransformer
from sklearn.decomposition import PCA
from sklearn.feature_selection import RFE
from sklearn.neural_network import MLPClassifier
from scipy.interpolate import interp1d

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
def preprocess(X, norm=True):

    df = pd.DataFrame()

    cat_cols = [c for c in X.select_dtypes(include='object').columns.tolist()\
                     if c!= 'patient_id']
    num_cols = X.select_dtypes(include='number').columns.tolist()

    # clipping
    X['alb'] = np.clip(X['alb'], 0.4, 5)
    # X['meanbp'] = np.clip(X['meanbp'], 20, 150)
    X['hrt'] = np.clip(X['hrt'], 0, 200)
    X['bili'] = np.clip(X['bili'], 0, 10)
    X['scoma'] = np.log1p(X['scoma'])

    # specific imputations
    X['alb'][X['alb'].isna()] = 3.5
    X['pafi'][X['pafi'].isna()] = 333.3
    X['bili'][X['bili'].isna()] = 1.01
    X['crea'][X['crea'].isna()] = 1.01
    X['bun'][X['bun'].isna()] = 6.65
    X['wblc'][X['wblc'].isna()] = 9.0
    X['urine'][X['urine'].isna()] = 2502

    for c in num_cols:
        x = X[c]
        x[np.isnan(x)] = np.nanmedian(x)
        df[c] = x
        # norm
        df[c] = (df[c]-df[c].median())/np.std(df[c])

    for c in cat_cols:
        x = X[c]
        x[x.isna()] = x.mode()
        for val in np.sort(np.array(x.unique(),dtype=str)):
            df[c+'-'+str(val)] = (x==val)

    # risk factors, one by one, 
    # see 
    # The SUPPORT Prognostic Model
    #   Objective Estimates of Survival for Seriously III Hospitalized Adults
    col = 'meanbp'
    func = interp1d([-10, 60, 200], [1.5, 0, 0]) 
    df['risk-%s' % col] = func(X[col])
    col = 'hrt'
    func = interp1d([-0.1, 90, 130, 301], [0.8, 0, 0.4, 0.4])
    df['risk-%s' % col] = func(X[col])
    col = 'pafi'
    func = interp1d([11, 200, 900], [0.8, 0, 0])
    df['risk-%s' % col] = func(X[col])
    col = 'crea'
    func = interp1d([0, 1.1, 3.4, 15, 30], [0.4, 0, 0.5, 0.0, 0])
    df['risk-%s' % col] = func(X[col])
    col = 'sod'
    func = interp1d([109, 137, 181], [0.7, 0, 0.4])
    df['risk-%s' % col] = func(X[col])
    col = 'bili'
    func = interp1d([0, 7, 64], [0., 0.4, 0.4])
    df['risk-%s' % col] = func(X[col])
    col = 'temp'
    func = interp1d([31, 34, 36.7, 42], [0.5, 0.5, 0, 0])
    df['risk-%s' % col] = func(X[col])
    col = 'resp'
    func = interp1d([-1, 20, 60, 100], [0.4, 0, 0.4, 0.4])
    df['risk-%s' % col] = func(X[col])
    col = 'alb'
    cond = (X['dzgroup']=='Lung Cancer') | (X['dzgroup']=='Colon Cancer')
    df['risk-alb-cancer'] = 0*df['alb']
    func = interp1d([0, 1.5, 4.5, 40], [2, 2, -1, -1])
    df['risk-alb-cancer'][cond] = func(X[col][cond])
    col = 'alb'
    cond = (X['dzclass']=='COPD/CHF/Cirrhosis')
    df['risk-alb-copd'] = 0*df['alb']
    func = interp1d([0, 2, 4, 40], [0.5, 0.5, -0.5, -0.5])
    df['risk-alb-copd'][cond] = func(X[col][cond])

    for k in [kk for kk in df if df[kk].dtype==bool]:
        df[k] = 1*df[k]

    return df

# %%

# Pipeline: scaling + MLP
pipe = Pipeline([
    ("pca", PCA(n_components=55)),
    ("rfe", RFE(n_features_to_select=20, estimator=model)),
    ("mlp", MLPClassifier(
        max_iter=500,
        early_stopping=True,
        n_iter_no_change=20,
        random_state=42,
    ))
])

# Grid of regularization values to scan
param_grid = {
    "mlp__alpha": np.logspace(-6, 1, 8),   # 1e-6 to 10
    "mlp__hidden_layer_sizes": [
        (64,),
        (128,),
        (64, 32)
    ],
    "mlp__learning_rate_init": [1e-3, 5e-4]
}

# Cross-validation
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

# Grid search
grid = GridSearchCV(
    estimator=pipe,
    param_grid=param_grid,
    scoring="f1_macro",
    cv=cv,
    n_jobs=-1,
    verbose=2,
    refit=True
)

df = preprocess(pd.read_csv('X_train.csv'))
df['target'] = LabelEncoder().fit_transform(pd.read_csv('y_train.csv')['sfdm2'])

# Fit search
grid.fit(
    df.loc[:,df.columns!='target'], df['target'])

# Best parameters
print("Best parameters:")
print(grid.best_params_)

print("\nBest CV macro F1:")
print(grid.best_score_)

# %%