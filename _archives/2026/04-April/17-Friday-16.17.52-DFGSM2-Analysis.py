
# %%
from DFGSM2_Project import *

# without preprocessing
p = Preprocess(pd.read_csv('X_train.csv'),
                 norm=False, transform=False)
dfO = p.df
# with preprocessing
p = Preprocess(pd.read_csv('X_train.csv'),
                 norm=True, transform=True)
dfN = p.df

for df in [dfO, dfN]:
    df['target'] = \
        build_target(pd.read_csv('y_train.csv'))

def show(col):
    fig, ax = plt.subplots(1, 2, figsize=(10,4))
    args = dict(x=col, hue='target', stat='density')
    sns.histplot(data=dfO.sort_values(by='target'), **args, ax=ax[0])
    ax[0].annotate('missing: %i ' % dfO[col].isna().sum(), (1, 0.1), xycoords='axes fraction', ha='right')
    sns.histplot(data=dfN.sort_values(by='target'), **args, ax=ax[1])
    for a, title in zip(ax, ['before', 'after']):
        a.set_title(title)
    return fig

# %%
show('hrt')

# %% [markdown]

# NOTE:
#       ADL: Activity of Daily Living 
#       A score of 6 indicates the patient is independent, 4 indicates the patient has moderate impairment, and 0 indicates the patient is very dependent. Katz S, Downs TD, Cash HR, et al: Progress in the development of the index of ADL.
# 

String = """
2	id	Identifiant unique du patient
3	age	Âge du patient en années
4	death	Décès à tout moment jusqu'à la date de clôture du NDI (31 décembre 1994)
5	sex	Sexe du patient (male / female)
6	hospdead	Décès survenu à l'hôpital (variable binaire cible)
7	slos	Nombre de jours entre l'entrée dans l'étude et la sortie de l'hôpital
8	d.time	Durée totale de suivi en jours
9	dzgroup	Sous-catégorie de maladie parmi 8 groupes (ex. ARF/MOSF w/Sepsis
10	dzclass	Catégorie de maladie parmi 4 classes (ARF/MOSF
11	num.co	Nombre de comorbidités simultanées (valeur ordinale
12	scoma	Score de Glasgow Coma Scale au jour 3 de l'étude
13	avtisst	Score TISS (Therapeutic Intervention Scoring System) moyen sur la durée de séjour
14	hday	Jour d'hospitalisation auquel le patient est entré dans l'étude
15	charges	Charges hospitalières totales en dollars
16	totcst	Coût total de l'hospitalisation (méthode de microcosting détaillé)
17	totmcst	Coût total estimé par ratio coûts/charges
18	race	Race / ethnie du patient
19	income	Revenu annuel autodéclaré du patient (variable catégorielle)
20	edu	Niveau d'éducation du patient en années
21	sfdm2	Incapacité fonctionnelle sévère à 2 mois évaluée sur une échelle ordinale 
22	adlp	Score des activités de la vie quotidienne (ADL) avant l'hospitalisation
23	adls	Score ADL avant l'hospitalisation par les Proches
24	adlsc	Score ADL cible utilisé dans les modèles en cas de comorbidité
25	urine	Débit urinaire sur 24 heures  (mL/24h)
26	ph	pH artériel 
27	pco2	Pression partielle en CO2 (mmHg) 
28	pafi	Ratio PaO2/FiO2 (indicateur de la fonction respiratoire)
29	alb	Albumine sérique (g/dL), faible = maladie du foie ; maladie rénale ; malnutrition
30	bili	Bilirubine sérique (mg/dL), haute = maladie du foie 
31	crea	Créatinine sérique (mg/dL), haute = dysfonction rénale 
32	bun	Azote uréique sanguin BUN (mg/dL), haut -> dysfonctionnement rénal (peut-être) 
33	wblc	Numération des globules blancs (milliers/µL), haut/bas -> infection / pb immun 
34	hrt	Fréquence cardiaque (battements/min) 
35	resp	Fréquence respiratoire (respirations/min) 
36	temp	Température corporelle (°C) 
37	meanbp	Pression artérielle moyenne (mmHg) 
38	wt	Poids corporel du patient (kg)
39	sod	Sodium sérique (mEq/L) 
40	sps	Score de physiologie SUPPORT calculé au jour 3
41	aps	Score de physiologie APACHE III calculé au jour 3
42	surv2m	Probabilité de survie à 2 mois estimée par le modèle pronostique SUPPORT
43	surv6m	Probabilité de survie à 6 mois estimée par le modèle pronostique SUPPORT
44	diabetes	Présence du diabète comme comorbidité (binaire)
45	dementia	Présence de démence comme comorbidité (binaire)
46	ca	Statut cancéreux du patient (aucun / solide localisé / métastatique)
47	prg2m	Estimation du médecin de la probabilité de survie du patient à 2 mois
48	prg6m	Estimation du médecin de la probabilité de survie du patient à 6 mois
49	dnr	Existence d'un ordre DNR (Do Not Resuscitate) pour le patient (binaire)
50	dnrday	Jour auquel l'ordre DNR a été posé (valeur négative si antérieur à l'entrée dans l'étude)
"""
keys = {}
for s in String.split('\n')[1:-1]:
    col = s.split('\t')[1]
    value = s.split('\t')[2]
    keys[col] = value

# %%
fig, ax = plt.subplots(1, figsize=(8.27, 11.69))
plt.subplots_adjust(left=0.8, right=0.9)
# df = df.drop('patient_id', axis=1)

CorrMatrix = np.zeros((len(df.columns)-1, 4))
Cols = []
for c, col in enumerate(df.columns[:-1]):
    for i, t in enumerate(\
        ['no_disability', 'moderate_disability', 'severe_disability', 'dead']):
        tt = (y_train['sfdm2']==t)
        cond = ~np.isnan(df[col])
        CorrMatrix[c,i] = np.log1p(np.abs(np.corrcoef(df[col][cond], tt[cond])[0,1])**.5)*\
                    np.sign(np.corrcoef(df[col][cond], tt[cond])[0,1])

    Cols.append(col)

min, max = np.nanmin(CorrMatrix), np.nanmax(CorrMatrix)
print(min, max)
ax.imshow(CorrMatrix, cmap=plt.cm.PiYG, vmin=min, vmax=max)
ax.set_yticks(range(len(Cols)))
ax.set_yticklabels(['%s - %s ' % (keys[c] if c in keys else '', c) for c in Cols])
ax.set_xticks(range(4))
ax.set_xticklabels(\
     ['none', 'moderate', 'severe', 'dead'],
     rotation=90)



# %%
sns.histplot(data=dfN.sort_values(by='target'), x='hrt-square', hue='target')
# ax[0].legend()
# ax[1].legend(loc=(1,.3))
# fig, ax = plt.subplots(1, 2)
# sns.boxplot(data=dfO, x=col, hue='target', ax=ax[1])

plt.show()
# %%
# for col in num_cols:
#     show(col)
# %%
