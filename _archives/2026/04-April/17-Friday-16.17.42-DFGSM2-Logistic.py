# %%

from DFGSM2_Project import *

model = LogisticRegression(max_iter=2000, 
                           random_state=1, 
                           C=0.016297508346206444,
                           penalty='elasticnet',
                           l1_ratio=0.5,
                           solver='saga',
                           class_weight='balanced')

df = p.tf(pd.read_csv('X_train.csv'))

model.fit(df.loc[:,df.columns!='target'], 
          pd.read_csv('y_train.csv')['sfdm2'])

scores = cross_val_score(model, 
                         df.loc[:,df.columns!='target'], 
                            pd.read_csv('y_train.csv')['sfdm2'],
                         cv=5, scoring='f1_macro')
print(f'F1-macro en validation croisée : {scores.mean():.3f} (+/- {scores.std():.3f})')

# %%
N=10
for c, classs in enumerate(model.classes_):

    # N = np.sum(model.coef_[c]>1e-2)

    fig, ax = plt.subplots()
    isorted = np.argsort(model.coef_[c])
    ax.barh(range(N), np.abs(model.coef_[c][isorted[:N]]))
    ax.set_yticks(range(N))
    ax.set_yticklabels([df.columns[i] if (np.abs(model.coef_[c][i])>1e-4) else '' for i in isorted[:N] ])
    # ax.set_yticklabels([df.columns[i] for i in isorted[:N] ])
    ax.set_title(classs)

# %%
y_pred = model.predict(df)
print(classification_report(y_train['sfdm2'], y_pred))

# %%

grid = GridSearchCV(
    estimator=model,
    param_grid={"C": np.logspace(-3, -0.5, 100),
                "random_state":[1,2,3],
                "max_iter":[2000], 
                "class_weight":['balanced']},
    cv=5,
    scoring="f1_macro",
    n_jobs=-1
)
grid.fit(df.loc[:,df.columns!='target'], 
            pd.read_csv('y_train.csv')['sfdm2'])

print("Best params:", grid.best_params_)
print("Best CV score:", grid.best_score_)


# %%
# # SUBMISSION 
df = p.tf(pd.read_csv('X_test.csv'))

submission = pd.DataFrame({
    'patient_id': pd.read_csv('X_test.csv')['patient_id'],
    'sfdm2': grid.predict(df)
})
submission.to_csv('submission.csv', index=False)
print('\n submission file written !')
"""


# # %%
# from sklearn.feature_selection import RFE
# model = LogisticRegression(max_iter=2000, 
#                            class_weight='balanced')
#                         #    class_weight=\
#                         #    {'dead':0.1, 
#                         #     'severe_disability':0.4, 
#                         #     'no_disability':0.2,
#                         #     'moderate_disability':0.8})

# pipeline = Pipeline(steps=[
#     # ("pca", PCA(n_components=20)),
#     # ("rfe", RFE(n_features_to_select=20, estimator=model)),
#     ("pol", PolynomialFeatures(degree=2)),
#     ("model", LogisticRegression(max_iter=2000, 
#                                  C=1e-2,
#                                  class_weight='balanced'))
# ])

# scores = cross_val_score(pipeline, 
#                 preprocess(pd.read_csv('X_train.csv')),
#                     pd.read_csv('y_train.csv')['sfdm2'],
#                          cv=5, scoring='f1_macro', n_jobs=-1)
# print(f'F1-macro en validation croisée : {scores.mean():.3f} (+/- {scores.std():.3f})')

# # %%
# param_grid = {
#     "model__C": np.logspace(0, -2, 50),
#     "model__random_state": [1,2,3],
#     # "rfe__n_features_to_select":[30, 35, 40],
# }

# grid = GridSearchCV(
#     estimator=pipeline,
#     param_grid=param_grid,
#     cv=5,
#     scoring="f1_macro",
#     n_jobs=-1
# )

# grid.fit(
#     preprocess(pd.read_csv('X_train.csv')),
#          pd.read_csv('y_train.csv')['sfdm2'])

# print("Best params:", grid.best_params_)
# print("Best CV score:", grid.best_score_)

# # %%
# # df1 = preprocess(pd.read_csv('X_train.csv'))


# # %%
# # model = LogisticRegression(max_iter=2000, 
# #                            random_state=12, 
# #                            C=1e-2,
# #                            class_weight='balanced')
# model = RandomForestClassifier(max_depth=5)
# model.fit(
#     preprocess(pd.read_csv('X_train.csv')),
#          pd.read_csv('y_train.csv')['sfdm2'])

# # Validation croisée sur le train (F1-macro)
# scores = cross_val_score(model, X_train_scaled, y_train['sfdm2'], 
#                          cv=5, scoring='f1_macro')
# print(f'F1-macro en validation croisée : {scores.mean():.3f} (+/- {scores.std():.3f})')

# # %%
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import RandomizedSearchCV, GridSearchCV, StratifiedKFold
# from scipy.stats import uniform, randint
# param_dist = {
#     "n_estimators":      randint(100, 400),
#     "max_depth":         [5, 10],
#     "min_samples_split": randint(5, 20),
#     "min_samples_leaf":  [5, 10],
#     "max_features":      ["sqrt", "log2", 0.1, 0.2, 0.3],
#     "max_samples":       uniform(0.6, 0.2),      # bagging fraction
#     "class_weight":      ["balanced", "balanced_subsample"],
#     "criterion":         ["gini", "entropy"],
# }

# cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=12)

# random_search = RandomizedSearchCV(
#     estimator=RandomForestClassifier(random_state=12, n_jobs=-1),
#     param_distributions=param_dist,
#     n_iter=200,            
#     scoring="f1_macro",     
#     cv=cv,
#     verbose=2,
#     random_state=42,
#     n_jobs=-1,
#     return_train_score=True,
# )

# random_search.fit(
#     preprocess(pd.read_csv('X_train.csv')),
#          pd.read_csv('y_train.csv')['sfdm2'])

# print("Best params:", random_search.best_params_)
# print("Best CV score:", random_search.best_score_)


# # %%
# X_test_scaled = pipeline.transform(X_test)
# y_pred = random_search.predict(X_test_scaled)

# submission = pd.DataFrame({
#     'patient_id': test_ids,
#     'sfdm2': y_pred
# })
# submission.to_csv('submission.csv', index=False)
# print(f'Soumission sauvegardée : {len(submission)} prédictions')
# print(f'\nDistribution des prédictions :')
# print(submission['sfdm2'].value_counts())
# print(f'\nAperçu :')
# submission.head()
# # -

# # %%
# X_test_scaled = pipeline.transform(X_test)


# # %%
# # pipeline.fit(X_train)
# # X_train = pipeline.fit_transform(X_train, y_train)
# X_train_scaled = pipeline.fit_transform(X_train, y_train)
# print(f'Train : {nX_train.shape[0]} patients, {nX_train.shape[1]} variables')
# # X_train[num_cols].isna().sum(axis=1)
# # np.isnan(np.array(X_train)).sum(axis=1)

# # %%

# df = pd.DataFrame(X_train)
# df['target'] = y_train['sfdm2']

# import seaborn as sns
# sns.histplot(df, x='age', hue='target')


# # %%
# # ### 5.2 Prétraitement

# # %%
# # Sauvegarder les patient_id du test pour la soumission
# test_ids = X_test['patient_id'].copy()

# # Supprimer patient_id (ce n'est pas une variable prédictive)
# X_train = X_train.drop(columns=['patient_id'])
# X_test = X_test.drop(columns=['patient_id'])
# target = y_train['sfdm2']

# # Identifier les colonnes catégorielles et numériques
# cat_cols = X_train.select_dtypes(include='object').columns.tolist()
# num_cols = X_train.select_dtypes(include='number').columns.tolist()
# print(f'Variables catégorielles ({len(cat_cols)}) : {cat_cols}')
# print(f'Variables numériques ({len(num_cols)}) : {num_cols}')

# # %%
# # Encoder les variables catégorielles
# encoders = {}
# for col in cat_cols:
#     le = LabelEncoder()
#     combined = pd.concat([X_train[col], X_test[col]]).astype(str)
#     le.fit(combined)
#     X_train[col] = le.transform(X_train[col].astype(str))
#     X_test[col] = le.transform(X_test[col].astype(str))
#     encoders[col] = le

# # Imputer les valeurs manquantes par la médiane (calculée sur le train)
# medians = X_train.median()
# X_train = X_train.fillna(medians)
# X_test = X_test.fillna(medians)

# # Standardiser
# scaler = StandardScaler()
# X_train_scaled = scaler.fit_transform(X_train)
# X_test_scaled = scaler.transform(X_test)
# # -

# # ### 5.3 Entraînement et évaluation

# # %%
# model = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
# model.fit(X_train_scaled, target)

# # Validation croisée sur le train (F1-macro)
# scores = cross_val_score(model, X_train_scaled, target, cv=5, scoring='f1_macro')
# print(f'F1-macro en validation croisée : {scores.mean():.3f} (+/- {scores.std():.3f})')
# # -

# # ### 5.4 Générer la soumission

# # %%
# X_test_scaled = pipeline.fit_transform(X_test)
# y_pred = grid.predict(X_test_scaled)

# submission = pd.DataFrame({
#     'patient_id': test_ids,
#     'sfdm2': y_pred
# })
# submission.to_csv('submission.csv', index=False)
# print(f'Soumission sauvegardée : {len(submission)} prédictions')
# print(f'\nDistribution des prédictions :')
# print(submission['sfdm2'].value_counts())
# print(f'\nAperçu :')
# submission.head()
# # %%

# df['target'] = (y_train['sfdm2']=='dead')

# # %%

# # %%
# df['income'].unique()
# df['income-num'] = np.nan+0*df['age']
# # print(df['income-num'])
# for i, inc in enumerate(['under $11k', '$25-$50k', '$11-$25k', '>$50k']):
#     cond = (df['income']==inc)
#     df['income-num'][cond] = i

# # %%
# fig, ax = plt.subplots()
# sns.histplot(data=df, x='edu', hue='income')
# # ax.scatter(df['income-num'], df['edu'])

# # %%
# df = pd.DataFrame(X_train)
# df['target'] = y_train['sfdm2']
# # %%
# sns.histplot(data=df, x='scoma', hue='target')

# # %%
# df['log-scoma'] = np.log1p(df['scoma'])
# sns.histplot(data=df, x='log-scoma', hue='target')

# # %%
# sns.heatmap(df[['age', 'avtisst', 'log-scoma', 'target']].corr(),
#             cmap='coolwarm', center=0, fmt='.2f', annot=True)
# # %%
"""
