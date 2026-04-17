# %%
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder,\
      OneHotEncoder, OrdinalEncoder, PolynomialFeatures

from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.feature_selection import RFE
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
class Preprocess:

    def __init__(self, X,
                 norm=True,
                 risk=True,
                 transform=True):

        self.df = pd.DataFrame()
        self.norm, self.risk, self.transform = norm , risk, transform
        self.df = self.tf(X)

    def tf(self, X):

        df = pd.DataFrame()

        norm, risk, transform = self.norm, self.risk, self.transform

        cat_cols = [c for c in X.select_dtypes(include='object').columns.tolist()\
                        if c not in ['patient_id', 'target']]
        num_cols = X.select_dtypes(include='number').columns.tolist()

        # clipping
        # X['meanbp'] = np.clip(X['meanbp'], 20, 150)

        if transform:

            # 
            df['no-adlp'] = ~(X['adlp'].isna())

            # hrt
            X['hrt'] = np.clip(X['hrt'], 40, 200)
            X['hrt-square'] = (X['hrt']-98)**2
            num_cols.append('hrt-square')

            # temp
            X['temp-square'] = np.log1p((X['temp']-37.09)**2)
            num_cols.append('temp-square')

            # wblc
            X['wblc'][X['wblc'].isna()] = 10.696287935163905
            X['wblc'] = np.clip(X['wblc'], 0, 50)
            X['wblc-square'] = np.log1p((X['wblc']-10.7)**2)
            num_cols.append('wblc-square')

            # scoma
            X['scoma'] = np.log1p(X['scoma'])

            # bun
            X['bun'][X['bun'].isna()] = 6.65
            X['bun'] = np.log1p(X['bun'])

            # Urine preprocessing
            X['urine'] = np.log1p(X['urine'])
            X['urine'][X['urine'].isna()] = np.log1p(2502)
            X['urine'] = np.clip(X['urine'], 6.75, 8.75)

            # Glucose
            X['glucose'] = np.log1p(X['glucose'])
            X['glucose'] = np.clip(X['glucose'], 3, 6.5)

            # pH
            X['ph-square'] = np.log1p(np.log1p((X['ph']-7.4)**2))
            num_cols.append('ph-square')

            # sod
            X['sod-square'] = np.log1p((X['sod']-137)**2)
            X['sod-square'] = np.clip(X['sod-square'], 2, 7)
            num_cols.append('sod-square')

            # crea
            X['crea'][X['crea'].isna()] = 1.01
            X['crea'] = np.clip(X['crea'], 0, 15) 
            X['crea'] = np.log1p(X['crea'])

            # bili
            X['bili'][X['bili'].isna()] = 1.01
            X['bili'] = np.log1p(np.log1p(X['bili']))
            # X['bili'] = np.clip(X['bili'], 0, 10)

            # alb
            X['alb'][X['alb'].isna()] = 3.5
            X['alb'] = np.clip(X['alb'], 0.4, 5)

            # pafi
            X['pafi'][X['pafi'].isna()] = 333.3
            X['pafi'] = np.clip(X['pafi'], 0, 650)

        for c in num_cols:

            if not hasattr(self, '%s-median' % c):
                setattr(self, '%s-median' % c, np.nanmedian(X[c]))
                setattr(self, '%s-mean' % c, np.nanmean(X[c]))
                setattr(self, '%s-std' % c, np.nanstd(X[c]))

            if transform:
                X[c][X[c].isna()] = getattr(self, '%s-median' % c)

            # put to df and normalize (X remain un-normalized)
            df[c] = X[c]
            if norm:
                mean = getattr(self, '%s-mean' % c)
                std = getattr(self, '%s-std' % c)
                df[c] = (df[c]-mean)/std

        for c in cat_cols:
            if not hasattr(self, '%s-mode' % c):
                setattr(self, '%s-mode' % c, X[c].mode())
            X[c][X[c].isna()] = getattr(self, '%s-mode' % c)
            for val in np.sort(np.array(X[c].unique(),dtype=str)):
                df[c+'-'+str(val)] = (X[c]==val)

        # ==== risk factors, one by one, ====
        # see 
        # The SUPPORT Prognostic Model
        #   Objective Estimates of Survival for Seriously III Hospitalized Adults
        if risk:
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
            df['risk-alb-cancer'] = 0*X['alb']
            func = interp1d([0, 1.5, 4.5, 40], [2, 2, -1, -1])
            df['risk-alb-cancer'][cond] = func(X[col][cond])
            col = 'alb'
            cond = (X['dzclass']=='COPD/CHF/Cirrhosis')
            df['risk-alb-copd'] = 0*X['alb']
            func = interp1d([0, 2, 4, 40], [0.5, 0.5, -0.5, -0.5])
            df['risk-alb-copd'][cond] = func(X[col][cond])

        return df
    

def build_target(y):
    target = y['sfdm2']
    for i, t in enumerate([\
         'no_disability',
         'moderate_disability',
         'severe_disability', 
         'dead'
        ]):
        target[target==t] = '%i-%s' % (i+1, t)
    return target


# df = preprocess(pd.read_csv('X_train.csv'))

# df_train = preprocess(pd.read_csv('X_train.csv'))
p = Preprocess(pd.read_csv('X_train.csv'))
df = p.df
# df['target'] = build_target(pd.read_csv('y_train.csv'))
X_train = pd.read_csv('X_train.csv')

