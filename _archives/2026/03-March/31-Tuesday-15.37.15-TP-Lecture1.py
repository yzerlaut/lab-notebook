# %%
import plot_tools as pt
import numpy as np

np.random.seed(2)

x = np.linspace(0, 2, 20)
def gen(x):
    return .6*np.random.randn(len(x))+x**2
y = gen(x) 
x2 = np.linspace(x.min(), x.max(), 1000)

fig, AX = pt.figure(axes=(5,1))
AX[0].scatter(x, y)
pt.set_plot(AX[0], xlabel='feature', ylabel='target',
            ylim=[-2,5],
            xticks=[0,1,2])

for ax, p in zip(AX[1:],
            [np.polyfit(x, y, 1),
                np.polyfit(x, y, 2),
                    np.polyfit(x, y, 8),
                        np.polyfit(x, y, len(x))]):

    ax.scatter(x, y)
    ax.plot(x2, np.polyval(p, x2), 'r-')
    ax.set_title(\
        'degree: %i\n' % (len(p)-1)+\
        'loss= %.2f ' % np.mean((y-np.polyval(p,x))**2))
    pt.set_plot(ax, xlabel='feature', 
            ylim=[-2,5],
            xticks=[0,1,2])

# %%
# Train Test Split
np.random.seed(2)
x1 = np.linspace(0, 2, 20)
x2 = np.linspace(0.2, 1.8, 6)
y1, y2 = gen(x1), gen(x2)
x = np.linspace(0, 2, 1000)

fig, AX = pt.figure(axes=(3,2), wspace=0.3, hspace=0.3)

AX[0][0].scatter(x1, y1, s=2, color='tab:orange')
AX[1][0].scatter(x2, y2, s=2, color='tab:blue')
pt.annotate(AX[0][0], 'Train', 
    (0.1,.8), va='top', color='tab:orange', fontsize=8)
pt.annotate(AX[1][0], 'Test', 
    (0.1,.8), va='top', color='tab:blue', fontsize=8)

for a, deg in enumerate([2, 20]):

    # AX[0][a].scatter(list(x1)+list(x2), 
    #             list(y1)+list(y2), s=2)

    train = np.random.choice(np.arange(len(x)), int(len(x)*.8), replace=False)
    iTrain = np.zeros(len(x), dtype=bool)
    iTrain[train] = True
    AX[0][a+1].scatter(x1, y1, s=2, color='tab:orange')
    AX[1][a+1].scatter(x2, y2, s=2, color='tab:blue')

    pol = np.polyfit(x1, y1, deg)
    for ax in [AX[0][a+1], AX[1][a+1]]:
        ax.plot(x, np.polyval(pol, x), 'r-', lw=0.5)

    AX[0][a+1].set_title('degree: %i' % deg)

    pt.annotate(AX[0][a+1],
        'loss= %.1f ' % np.mean((y1-np.polyval(pol,x1))**2),
        (0.2,.9), va='top', color='tab:orange', fontsize=7)
    pt.annotate(AX[1][a+1],
        'loss= %.1f ' % np.mean((y2-np.polyval(pol,x2))**2),
        (0.2,.9), va='top', color='tab:blue', fontsize=7)

for a in range(3):
    for b in range(2):
        pt.set_plot(AX[b][a], 
                    ylabel='target' if a==0 else None,
                    yticks_labels=[] if a!=0 else None, 
                    xticks_labels=[] if b==0 else None, 
                    xlabel='feature',#,#,#,#,#,#,#,#,# if b==0 else '', 
                ylim=[-2,5],
                xticks=[0,1,2])



# %%
import plot_tools as pt
import numpy as np

np.random.seed(0)

x = np.linspace(-1, 1, 10)
y = .5*np.random.randn(10)+x

for p in [-x, np.polyval(np.polyfit(x, y, 1),x)]:

    fig, ax = pt.figure(ax_scale=(1.1,1.1))
    ax.scatter(x, y)
    ax.plot(x, p, 'r-')
    for xx, yy, pp in zip(x, y, p):
        ax.plot([xx,xx], [yy, pp], 'r:', lw=0.3)
    ax.set_title(\
        'loss= %.2f ' % np.mean((y-np.polyval(p,x))**2))
    pt.set_plot(ax, xlabel='feature', ylabel='target',
                yticks=[-1,0,1],
                xticks=[-1,0,1])

# %%
fig, ax = pt.figure(ax_scale=(1,1.1))
x = np.linspace(-3,3)
for i, a, b in zip(range(4), [1,3,3,-2], [4, 4, 2, 1]):
    ax.plot(x, a*x+b, color=pt.tab10(i))
    pt.annotate(ax, i*'\n'+'$a$=%i,$b$=%i' % (a,b), (1,1), va='top', color=pt.tab10(i))
pt.set_plot(ax, xlabel='input', ylabel='output',
            title='linear function\n2 params: slope $a$, intercept $b$')

# %%
fig, ax = pt.figure(ax_scale=(1,1.1))
x = np.linspace(-3,3)
for i, a, b, c in zip(range(3), 
                      [1,1,-0.5], 
                      [-2, 1, 0],
                      [1,-2,3]):
    ax.plot(x, a*x**2+b*x+c, color=pt.tab10(i))
    pt.annotate(ax, i*'\n'+'$a$=%.1f,$b$=%i,$c$=%i' % (a,b,c), (1,1), va='top', color=pt.tab10(i))
pt.set_plot(ax, xlabel='input', ylabel='output',
            title='polynom, y=$a$x$^2$+$b$x+$c$\n3 params: $a$, $b$, $c$')
# %%
import numpy as np

# The target is a quantitative measure of disease progression 
#          one year after baseline.
# Concretely:
# It is a continuous numerical value (ranging roughly from 25 to 346)
# It reflects how much the diabetes worsened over one year
# It is a composite clinical score — not a single direct measurement like blood sugar

from sklearn.datasets import load_diabetes
data = load_diabetes(as_frame=True, scaled=False)
df = data['frame'] # df: dataframe
# df = np.round(df, 3) 
df

# %%
import matplotlib.pylab as plt
import seaborn as sns

# prepare figure
fig, AX = plt.subplots(5, 2, figsize=(5,7))
plt.subplots_adjust(wspace=1.0, hspace=0.8)

# loop over features
for i, column in enumerate(df.columns[:-1]):
    sns.scatterplot(data=df, 
                 x=column, y='target',
                 ax=AX[int(i%5)][int(i/5)])
    
# %%
# df['sex'][df['sex']==1] = 'F'
# df['sex'][df['sex']==2] = 'M'

fig, ax = plt.subplots(figsize=(4,3))
sns.histplot(data=df, 
             x='target',
             hue='sex',
             kde=True, 
             legend={'loc':(1.,0.5)},
            #  line_kws={'lw':3},
             ax=ax)
# ax.legend(loc=(1.0,0.5))

# %%
# separate features and target
X = df.loc[:, df.columns!='target'] # all but the target
y = df.loc[:, df.columns=='target'] # target only

# train/test split
from sklearn.model_selection import train_test_split
X_train, X_test,\
      y_train, y_test =\
                train_test_split(X, y,
                                test_size=0.20,
                                random_state=4)

# build model
from sklearn.linear_model import LinearRegression
model = LinearRegression()
# fit
model.fit(X_train, y_train)
# predict
y_pred = model.predict(X_test)
# evaluate using r2 score
from sklearn.metrics import r2_score
print('r2 score = %.2f' % r2_score(y_test, y_pred))

# %%
fig, ax = plt.subplots()
ax.bar(model.coef_)

###############
# %%
Z = {}
for feature, coef in zip(df.columns, model.coef_.flatten()):
    print(feature, coef)
    Z[feature] = [np.round(coef,2)]
import pandas as pd
pd.DataFrame(Z).T

########################################################
###    logistic regression #############################
########################################################
# %%
# TITANIC data
from sklearn.datasets import fetch_openml
titanic = fetch_openml(name='titanic', version=1, as_frame=True)
X, y = titanic.data[['pclass','age','sex','fare']], titanic.target

# %%
# # BREAST CANCER
import plot_tools as pt
import numpy as np
from sklearn.datasets import load_breast_cancer
data = load_breast_cancer(as_frame=True)
df = data['frame']
df


# %%
fig, AX = pt.figure(axes=(5,6), hspace=1.5,
                    right=2.5, ax_scale=(1.,1.))

# loop over features
for i, column in enumerate(df.columns[:-1]):
    AX[int(i%6)][int(i/6)].scatter(df[column], df['target'])
    pt.set_plot(AX[int(i%6)][int(i/6)],
                num_xticks=2,
                yticks=[0,1],
                yticks_labels=[] if int(i/6)!=0 else ['malignant', 'benign'],
                xlabel=column)

# %%
for cols in [
     ['worst radius','mean perimeter'],
     ['mean texture','worst area'],
                ]:
    fig, ax = pt.figure(ax_scale=(1.1,1.3))
    ax = sns.scatterplot(data=df,
                    x=cols[0], y=cols[1],
                    legend=False,
                    hue='target', ax=ax)
    for i, c, s in zip(range(2), ['k', 'tab:blue'], [' malignant', ' benign']):
        pt.annotate(ax, i*'\n'+s, (0,1.2), va='top', color=c)

# %%
column = 'worst radius'
fig, ax = pt.figure(ax_scale=(1.2,1.2))
ax.scatter(df[column], df['target'], alpha=.2, label='data')
from sklearn.linear_model import LinearRegression
X = df.loc[:, df.columns==column]
y = df.loc[:, df.columns=='target']
model = LinearRegression()
model.fit(X, y)
xx = np.linspace(X.min(), X.max())
ax.plot(xx, model.predict(xx), 'r-', label='linear regression')
ax.legend(frameon=False, loc=(0.1, 1.))
pt.set_plot(ax, 
            ylim=[-0.2,1.2],
            num_xticks=2,
            yticks=[0,1],
            yticks_labels=['(malignant) 0', '(benign) 1'],
            xlabel=column)

# %%
from sklearn.model_selection import train_test_split
fig, ax = pt.figure(ax_scale=(1.2,1.2))

X_train, X_test, y_train, y_test = train_test_split(X, y)
ax.scatter(X_train, y_train, alpha=.2, label='training')

from sklearn.linear_model import LogisticRegression
X = df.loc[:, df.columns==column]
y = df.loc[:, df.columns=='target']
model = LogisticRegression()#max_iter=1000, tol=1e-6)
model.fit(X_train, y_train)
xx = np.linspace(X.min(), X.max())
# ax.plot(xx, model.predict_proba(xx)[:,1], 'r-', label='logistic regression')
ax.scatter(X_test, model.predict_proba(X_test)[:,1], 
           alpha=.2, color='r', label='test (proba)')
ax.legend(frameon=False, loc=(-0.2, 1.2))
pt.set_plot(ax, 
            ylim=[-0.2,1.1],
            num_xticks=2,
            yticks=[0,1],
            yticks_labels=['(malignant) 0', '(benign) 1'],
            xlabel=column)


# %%
X, y = load_diabetes(return_X_y=True, as_frame=True, scaled=False)
X = X.loc[:, X.columns == 'bmi'] # keep only the Body Mass Index (most discriminating single feature)

fig, ax = pt.figure(ax_scale=(1.1,1.2))
ax.scatter(X, y, alpha=.1)
from sklearn.linear_model import LinearRegression
if True:
    model = LinearRegression()
    model.fit(X, y)
    ax.plot(X, model.predict(X), 'r-', lw=2)
pt.set_plot(ax, ['left', 'bottom'], 
            xlabel='body mass index', ylabel='diabetes prog.\n (clin. score)')

# %%

# "worst radius" = the average size of the 3 biggest cell nuclei measured in the image
# Malignant (cancerous) tumors tend to have larger and more irregular cell nuclei than benign ones. So a high "worst radius" value is a strong indicator of malignancy — which is exactly why it's the most discriminating single feature in the dataset.

from sklearn.datasets import load_breast_cancer
import numpy as np

X, y = load_breast_cancer(return_X_y=True, as_frame=True)
X = X.loc[:, X.columns == 'worst radius'] # keep only the Body Mass Index (most discriminating single feature)
# X = data.data[:, [0]]  # focusing on worst radius (feature la plus discriminante)
y = 1-y # SHIFT --> 1 = malignant, 0 = benign
fig, ax = pt.figure()
ax.scatter(X, y, alpha=.1)
pt.set_plot(ax, ['left', 'bottom'],
            xlabel='worst radius ($\mu$m)      ' ,
            yticks=[0,1], yticks_labels=['(benign) 0', '(malignant) 1'])

# %%
import pandas as pd
import seaborn as sns
sns.set_theme(font_scale=2)

df = pd.read_csv("https://raw.githubusercontent.com/yzerlaut/medical_datasets/main/diabetes/diabetes_train.csv")

sns.histplot(data=df, 
             x='BMI',
             hue='Diabetes',
             kde=True, 
             line_kws={'lw':3},
             bins=20)
# %%
import pandas as pd
import numpy as np
df = pd.read_csv("https://raw.githubusercontent.com/yzerlaut/medical_datasets/main/diabetes/diabetes_train.csv")
X = df.drop(['Diabetes'], axis=1)
y = df.loc[:, df.columns=='Diabetes']

# %%
from sklearn.model_selection import train_test_split
X_train, X_test,\
      y_train, y_test =\
                train_test_split(X, y,
                                test_size=0.20,
                                random_state=1)

# %%

from sklearn.linear_model import LogisticRegression

model = LogisticRegression(max_iter=5000)


# %%
model.fit(X_train, y_train)

# %%
y_pred = model.predict(X_test)

print(f"Predictions (first 10): {y_pred[:10]}")
print(f"Actual      (first 10): {y_test.values.flatten()[:10]}")
# %%
from sklearn.metrics import (accuracy_score, confusion_matrix, ConfusionMatrixDisplay,
                             classification_report, precision_score, recall_score, f1_score)
# %%
print(classification_report(y_test, y_pred))

# %%
print("Accuracy Score: %.3f " % accuracy_score(y_test, y_pred))
# %%
import plot_tools as pt
fig, ax = pt.figure(ax_scale=(1.3,1.3))
# import matplotlib.pylab as plt
# fig, ax = plt.subplots()
ConfusionMatrixDisplay.from_predictions(y_test, y_pred, 
                                        display_labels=['none  ', '  diabetes'],
                                        ax=ax, 
                                        cmap='Blues')
ax.set_title('Confusion Matrix')
# plt.show()
# %%
cm = confusion_matrix(y_test, y_pred)
print(f"Confusion matrix:\n{cm}\n")

# For the "malignant" class (class 0 = positive in medical context):
# With sklearn's convention: cm[0,0]=TN for class 1, but for class 0:
# We consider malignant (0) as the positive class
TN = cm[1, 1]  # benign predicted as benign
FP = cm[1, 0]  # benign predicted as malignant
FN = cm[0, 1]  # malignant predicted as benign
TP = cm[0, 0]  # malignant predicted as malignant

print(f"TP (malignant correctly detected): {TP}")
print(f"TN (benign correctly detected): {TN}")
print(f"FP (benign predicted as malignant): {FP}")
print(f"FN (malignant predicted as benign): {FN}")

# Manual computation
precision_manual = TP / (TP + FP)
recall_manual = TP / (TP + FN)
f1_manual = 2 * precision_manual * recall_manual / (precision_manual + recall_manual)

print(f"\n--- Manual computation (malignant class) ---")
print(f"Precision: {precision_manual:.4f}")
print(f"Recall:    {recall_manual:.4f}")
print(f"F1-score:  {f1_manual:.4f}")

# Verify with sklearn (pos_label=0 since malignant is class 0)
print(f"\n--- sklearn verification ---")

print(f"Accuracy  : {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision : {precision_score(y_test, y_pred):.4f}")
print(f"Recall    : {recall_score(y_test, y_pred):.4f}")
print(f"F1-score: : {f1_score(y_test, y_pred):.4f}")

# %%
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model_scaled = LogisticRegression(max_iter=5000)
model_scaled.fit(X_train_scaled, y_train)

y_pred_scaled = model_scaled.predict(X_test_scaled)

print(f"Accuracy (without scaling): {accuracy_score(y_test, y_pred):.4f}")
print(f"Accuracy (with scaling):    {accuracy_score(y_test, y_pred_scaled):.4f}")

print("\nConfusion matrix (with scaling):")
fig, ax = pt.figure(ax_scale=(1.3,1.3))
ConfusionMatrixDisplay.from_predictions(y_test, y_pred_scaled, 
                                        # display_labels=data.target_names, 
                                        ax=ax, cmap='Blues')
# plt.title('Confusion Matrix (with scaling)')
# plt.show()
# %%
# Compute correlation with target
correlations = df.corr()['Diabetes'].drop('Diabetes')
correlations = correlations.sort_values(ascending=False)
top_features = correlations.head(5).index.tolist()

# Heatmap of top features + target
fig, ax = pt.figure(ax_scale=(1.8,3))
# fig, ax = plt.subplots()
sns.heatmap(df[top_features + ['Diabetes']].corr(), 
            annot=True, fmt='.2f', cmap='coolwarm', center=0)
ax.set_title(
    'Correlation Heatmap (Top 5 Features + Target)')
# plt.tight_layout()

print("Top 5 features correlated with target:")
print(correlations.head(5))i

# %%
##################################################
###     Data Preprocessing    #####################
##################################################

# %%
from sklearn.datasets import fetch_openml
import pandas as pd
import seaborn as sns
sns.set_theme(font_scale=2)
# Load dataset
from sklearn.datasets import fetch_openml
titanic = fetch_openml(name='titanic', version=1, as_frame=True)
df = titanic.frame
df
# df = df[['education', 'marital-status', 'sex', 'workclass', 'native-country', 'occupation']]

# print(df[['education', 'marital-status', 'sex', 'workclass']].head(8))
# %%
df
# %%
# df['marital-status'].unique()
# %%
df.info()
# %%
# fig, ax = pt.figure()
sns.heatmap(df['age'].T,
            cbar=False)

# %%
# fig, ax = pt.figure()
sns.heatmap(df.isnull().T,
            cbar=False)
# ax.invert_yaxis()

# %%
import plot_tools as pt
import matplotlib.pylab as plt
fig, AX = plt.subplots(1, 4, figsize=(9,3))
plt.subplots_adjust(wspace=1.4)
for col, ax in zip(['age', 'fare', 'parch', 'sibsp'], AX):
    df[col].plot(kind='box', ax=ax)
# df['fare'].plot(kind='box', ax=ax)
# df[['fare', 'age']].plot(kind='box', subplots=True, layout=(1,2), figsize=(8,4), ax=ax)
# %%
# fig, AX = plt.subplots(1, 4, figsize=(7,3))
for col in ['pclass', 'sex', 'embarked', 'sibsp']:
    sns.catplot(df, x=col, kind='count', palette='pastel')
# %%
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
le.fit(['1st-class', '2nd-class', '3rd-class'])
le.fit([1, 2, 3])
df['class'] = le.transform(df['pclass'])
df['class']
# %%
from sklearn.preprocessing import OneHotEncoder
ohe = OneHotEncoder(handle_unknown='ignore')
ohe.fit(df['sex'])
# encoded = ohe.fit_transform(df[['sex', 'embarked']])
# df_encoded = pd.DataFrame(encoded) #, columns=ohe.get_feature_names_out())
#  = ohe.transform(df['sex'])

# %%
from sklearn.preprocessing import OneHotEncoder
ohe = OneHotEncoder()
encoded = ohe.fit_transform(df[['sex', 'embarked']])
pd.DataFrame(encoded)
# df_encoded = pd.DataFrame(encoded, columns=ohe.get_feature_names_out())

#
pd.get_dummies(df, columns=['sex', 'embarked'])


# %%
from sklearn.preprocessing import TargetEncoder
from sklearn.datasets import fetch_openml
import pandas as pd

titanic = fetch_openml(name='titanic', version=1, as_frame=True)
df = titanic.frame.dropna(subset=['survived', 'embarked'])

X = df[['embarked']]
y = df['survived'].astype(float)

enc = TargetEncoder()
X_encoded = enc.fit_transform(X, y)
# %%
X_encoded[:20,:]
# %%
X.head(20)
# %%
hash('Bari')

# %%
from scipy.stats import uniform
func = uniform(loc=0, scale=4)
# %%
y_pred = (df['sex']=='female') | (df['age']<15)

# %%
import numpy as np
from sklearn.metrics import classification_report
print(\
    classification_report(df['survived'].to_numpy(dtype=int), y_pred.to_numpy(dtype=int)))
# %%
print(np.sum(df['survived'].to_int()))

# %%
titanic = fetch_openml(name='titanic', version=1, as_frame=True)
df = titanic.frame
df = pd.get_dummies(df, columns=['embarked'], dtype=int)
df['sex'] = df['sex'].replace('female', 0)
df['sex'] = df['sex'].replace('male', 1)
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='mean')
# also: 'median', 'most_frequent'
df[['age']] = imputer.fit_transform(df[['age']])
df[['fare']] = imputer.fit_transform(df[['fare']])

df
# df = df.drop(['sex', 'name', 'home.dest', 'body', 'cabin', 'boat'], axis=1)

# %%
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
ohe = OneHotEncoder(sparse_output=False)
encoded = ohe.fit_transform(df['embarked'])
df = pd.DataFrame(encoded)
df

# %%
cond = (df.columns!='survived')\
      & (df.columns!='name')\
      & (df.columns!='cabin')\
      & (df.columns!='ticket')\
      & (df.columns!='body')\
      & (df.columns!='home.dest')\
      & (df.columns!='boat')

X = df.loc[:, cond]
y = df.loc[:, df.columns=='survived'].to_numpy(dtype=int)

# %%
X_train, X_test, y_train, y_test =\
    train_test_split(X, y, random_state=8)

from sklearn.tree import DecisionTreeClassifier, plot_tree
tree = DecisionTreeClassifier(max_depth=4)
tree.fit(X_train, y_train)
y_pred = tree.predict(X_test)

# Visualization
fig, ax = pt.figure(ax_scale=(5,7))
plot_tree(tree, filled=True, ax=ax)

# %%
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred))
# %%
from sklearn.ensemble import VotingClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression

model = VotingClassifier(estimators=[
    ('svm', SVC(kernel='rbf', C=1.0)),
    ('tree', DecisionTreeClassifier(max_depth=4)),
    ('lr', LogisticRegression()),
], voting='hard')

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
# %%
print(classification_report(y_test, y_pred))

# %%
