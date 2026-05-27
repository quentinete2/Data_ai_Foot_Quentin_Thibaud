# Rapport EDA Approfondie - Phase 2.1
## Étape 2.1 : Validation de la Question Prédictive

Date : Mai 27, 2026  
Dataset : FIFA World Cup Matches (1930–2022)

---

## 📋 Résumé Exécutif

L'EDA approfondie a **VALIDÉ la question prédictive** avec quelques ajustements importants :

- ✅ **Cible (y)** : Bien définie et prévisible (result ∈ {0, 1, 2})
- ✅ **Features (X)** : 9 features sélectionnées avec corrélations significatives
- ⚠️ **Déséquilibre des classes** : GRAVE (56.3% / 16.8% / 26.8%) → resampling requis
- ⚠️ **Multicolinéarité** : Élevée entre certains pairs → gérée par RandomForest
- ✅ **Qualité des données** : Excellente (aucune valeur manquante, outliers gérables)

---

## 1. CIBLE (y) — Analyse Complète

### Définition
```
result ∈ {0, 1, 2}
  0 = Home Win (victoire équipe domicile)
  1 = Draw (match nul)
  2 = Away Win (victoire équipe visiteur)
```

### Distribution des Classes

| Classe | Nom | Compte | % | Observation |
|--------|-----|--------|---|---|
| **0** | Home Win | 703 | 56.33% | **Majorité écrasante** |
| **1** | Draw | 210 | 16.83% | Classe minoritaire |
| **2** | Away Win | 335 | 26.84% | Classe modérée |

### Analyse du Déséquilibre

```
Ratio max/min : 3.35
Différence max-min : 39.5 points de %
```

**Diagnostic** : ⚠️ **Déséquilibre GRAVE**
- L'écart entre classe majority (56%) et minority (17%) > 25%
- RandomForest naturellement biaisé vers la classe 0

**Action recommandée** :
- [ ] Utiliser `class_weight='balanced'` dans RandomForestClassifier
- [ ] OU appliquer **SMOTE** (Synthetic Minority Over-sampling) en preprocessing
- [ ] Évaluer avec **F1-score (macro)** plutôt qu'accuracy seule

---

## 2. FEATURES (X) — Sélection et Analyse

### Features Sélectionnées (9 au total)

#### 📊 Statistiques Descriptives

| Feature | Mean | Std | Min | Max | Skew | Kurtosis |
|---------|------|-----|-----|-----|------|----------|
| **home_avg_goals** | 1.81 | 0.64 | 0.00 | 5.00 | +0.24 | 2.42 |
| **away_avg_goals** | 1.11 | 0.42 | 0.00 | 3.00 | +0.52 | 1.40 |
| **goal_diff** | 0.70 | 0.79 | -2.41 | 4.46 | +0.10 | 1.83 |
| **home_total_matches** | 38.10 | 28.34 | 1 | 106 | +0.95 | 0.28 |
| **away_total_matches** | 24.90 | 12.87 | 1 | 47 | +0.22 | -0.94 |
| **home_wins** | 24.67 | 21.75 | 0 | 79 | +1.14 | 0.71 |
| **away_wins** | 13.23 | 6.43 | 0 | 30 | +0.35 | 0.13 |
| **year** | 1993.33 | 22.84 | 1930 | 2022 | -0.91 | 0.11 |
| **count_teams** | 23.47 | 7.29 | 12 | 32 | -0.03 | -1.57 |

#### 🔗 Corrélations avec la Cible

| Feature | Corrélation | Force | Interprétation |
|---------|-------------|-------|---|
| **goal_diff** | **-0.444** | **Forte** | Plus high avg goals domicile → victoire domicile |
| **home_avg_goals** | **-0.355** | **Modérée** | Plus de buts domicile → victoire domicile |
| **away_avg_goals** | +0.294 | Modérée | Plus de buts visiteur → victoire visiteur |
| **year** | +0.270 | Modérée | Tendance temporelle (matchs plus récents biaisé vers visiteur) |
| **home_wins** | -0.251 | Modérée | Plus de victoires hist. → victoire domicile |
| **home_total_matches** | -0.233 | Faible | Expérience domicile → légère avantage domicile |
| **count_teams** | +0.207 | Faible | Plus d'équipes au tournoi → moins d'avantage domicile |
| **away_total_matches** | +0.165 | Faible | Expérience visiteur → légère avantage visiteur |
| **away_wins** | +0.014 | **Très faible** | Quasi nulle → envisager suppression |

---

## 3. Valeurs Manquantes — Analyse Complète

### Résultat

```
✓ Aucune valeur manquante détectée dans les 40 colonnes
✓ Pas de preprocessing requis pour NaN
```

**Impact** : ✅ Pas de perte de données, pas d'imputation nécessaire.

---

## 4. Outliers — Détection Box Plot

### Détection (IQR méthode : Q1 ± 1.5×IQR)

| Feature | Outliers | % du dataset | Action |
|---------|----------|---|---|
| **home_wins** | 106 | 8.49% | **À garder** (sports naturellement extrêmes) |
| **home_avg_goals** | 69 | 5.53% | À garder |
| **year** | 53 | 4.25% | À garder (matchs anciens, distributions légitimes) |
| **away_avg_goals** | 43 | 3.45% | À garder |
| **goal_diff** | 29 | 2.32% | À garder |
| **TOTAL** | **300** | **24.04%** | **Acceptable** |

**Diagnostic** : ⚠️ 24% d'outliers = beaucoup, mais LÉGITIME en contexte sportif
- Un match 7–0 n'est pas erreur, c'est réalité (ex: Australie 31–0 Samoa 2001)
- RandomForest robuste aux outliers (pas besoin de scaling)

**Décision** : ✅ **Garder tous les outliers** (pas de suppression/clipping)

---

## 5. Corrélations Entre Features — Multicolinéarité

### Paires de Haute Corrélation (|r| > 0.8)

| Feature 1 | Feature 2 | Corrélation | Sévérité | Recommandation |
|-----------|-----------|---|---|---|
| **home_total_matches** | **home_wins** | **0.989** | **CRITIQUE** | Considérer suppression une des deux |
| **home_avg_goals** | **goal_diff** | 0.849 | Haute | RandomForest gère bien |
| **away_total_matches** | **away_wins** | 0.866 | Haute | Considérer suppression une des deux |

### Analyse Détaillée

#### ⚠️ Problem 1 : `home_total_matches` ↔ `home_wins` (r = 0.989)

```
Interprétation : Plus une équipe joue (total_matches), plus elle gagne (wins)
→ LOGIQUE CIRCULAIRE (multicolinéarité quasi-parfaite)
```

**Options** :
1. **Supprimer `home_total_matches`** → garder `home_wins` (plus explicite)
2. Ou supprimer `home_wins` → garder `total_matches` (proxy d'expérience)
3. **Recommandation** : Garder `home_wins`, `away_wins` (statistiques explicites)

#### ⚠️ Problem 2 : `home_avg_goals` ↔ `goal_diff` (r = 0.849)

```
Interprétation : Plus on marque en moyenne, plus on a un but_diff positif
→ ATTENDU (but_diff dépend de avg_goals domicile)
```

**Décision** : RandomForest gère les corrélations modérées automatiquement
→ Garder les deux (complémentaires : attaque vs défense relative)

#### ⚠️ Problem 3 : `away_total_matches` ↔ `away_wins` (r = 0.866)

```
Même logique que Problem 1
```

**Recommandation** : Garder `away_wins`, considérer supprimer `away_total_matches`

---

## 6. Distributions des Features — Normalité & Skewness

### Interprétation Skewness

| Feature | Skew | Type | Implication |
|---------|------|------|---|
| home_avg_goals | +0.24 | Léger droit | OK, quasi-normal |
| away_avg_goals | +0.52 | Modéré droit | OK |
| goal_diff | +0.10 | Quasi-normal | ✅ Excellent |
| **home_wins** | **+1.14** | **Fortement droit** | Queue longue (équipes peu gagnantes) |
| **away_wins** | +0.35 | Léger droit | OK |
| **year** | **-0.91** | **Fortement gauche** | Plus de données récentes |
| count_teams | -0.03 | Parfaitement symétrique | ✅ Excellent |

**Impact** : RandomForest insensible à skewness → pas de preprocessing requis (pas de log transform)

---

## 7. Résumé Validé — Question Prédictive Finale

### ✅ CIBLE (y)

```
Nom           : result
Type          : Catégorique (multiclass)
Classes       : 3 (Home Win, Draw, Away Win)
Distribution  : 56.3% / 16.8% / 26.8% [GRAVE DÉSÉQUILIBRE]
Valeur/min    : Non-null
```

### ✅ FEATURES (X) — Version Finale

```
Recommandé (9 features) :
  1. home_avg_goals          (corr: -0.355)
  2. away_avg_goals          (corr: +0.294)
  3. goal_diff               (corr: -0.444) ← Plus forte
  4. home_wins               (corr: -0.251)
  5. away_wins               (corr: +0.014) ← Très faible
  6. year                    (corr: +0.270)
  7. count_teams             (corr: +0.207)
  8. home_total_matches      (corr: -0.233) ← Considérer suppression
  9. away_total_matches      (corr: +0.165) ← Considérer suppression

Alternative optimisée (7 features, multicolinéarité réduite) :
  1. home_avg_goals
  2. away_avg_goals
  3. goal_diff
  4. home_wins
  5. away_wins
  6. year
  7. count_teams
  [SUPPRIMER home_total_matches et away_total_matches pour réduire multicolinéarité]
```

### ✅ FAMILLE ML — CLASSIFICATION

```
Justification    : Y multiclasse (3 classes distinctes) → classification
Algorithme       : RandomForestClassifier (100 trees, max_depth=10)
Avantages RF     : Robuste multicolinéarité, outliers, pas de scaling
```

### ✅ MÉTRIQUES PRINCIPALES

```
Primaire   : Accuracy (56.3% baseline = toujours prédire classe 0)
Secondaire : F1-score (macro) — pour gérer déséquilibre
Tertaire   : Precision/Recall par classe
```

### ✅ DATA QUALITY

```
Total matches          : 1248
Valeurs manquantes     : 0 ✓
Outliers               : 300 (24%) → GARDÉS (légitime)
Multicolinéarité       : Modérée → Gérée par RF
Skewness               : Généralement faible → OK
```

---

## 8. Ajustements Requis pour l'Entraînement

### À Implémenter dans le Notebook

```python
# 1️⃣ Équiliber les classes
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    class_weight='balanced',  # ← IMPORTANT pour déséquilibre
    random_state=42
)

# 2️⃣ Évaluer correctement
from sklearn.metrics import classification_report, f1_score

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
print(f"F1-score (macro): {f1_score(y_test, y_pred, average='macro')}")

# 3️⃣ Features : envisager suppression optionnelle
# Option A : Garder 9 features (baseline)
# Option B : Supprimer home_total_matches, away_total_matches
```

### À Documenter dans la Prédiction

```
Limitations :
- Modèle biaisé vers prédiction "Home Win" (56% des données)
- Considérer SMOTE ou stratified cross-validation
- Accuracy seule insuffisante → priorité F1-score (macro)
```

---

## 9. ✅ Conclusion — Question Prédictive VALIDÉE

| Élément | Status | Note |
|---------|--------|------|
| **Cible bien définie** | ✅ | 3 classes, but clair |
| **Features pertinentes** | ✅ | Corrélations 0.014–0.444 avec y |
| **Données propres** | ✅ | 0 valeurs manquantes, outliers acceptables |
| **Famille ML justifiée** | ✅ | Classification multiclass |
| **Métrique appropriée** | ✅ | Accuracy + F1-score (macro) |
| **Ajustements nécessaires** | ⚠️ | class_weight='balanced' requis |

**Verdict** : 🚀 **PRÊT POUR L'ENTRAÎNEMENT DU MODÈLE (Étape 2.2)**

---

## Annexe : Commandes pour Visualisations Avancées

Pour générer les graphiques en Jupyter :

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Histogrammes des features
fig, axes = plt.subplots(3, 3, figsize=(15, 10))
features = ['home_avg_goals', 'away_avg_goals', 'goal_diff', 'home_total_matches', 
            'away_total_matches', 'home_wins', 'away_wins', 'year', 'count_teams']
for i, feature in enumerate(features):
    row, col = divmod(i, 3)
    axes[row, col].hist(X_eda[feature], bins=30, edgecolor='black')
    axes[row, col].set_title(f'{feature}\nskew={X_eda[feature].skew():.2f}')
    axes[row, col].set_xlabel('Valeur')
plt.tight_layout()
plt.show()

# Matrice de corrélation
fig, ax = plt.subplots(figsize=(12, 10))
X_with_target = X_eda.copy()
X_with_target['result'] = y_eda
sns.heatmap(X_with_target.corr(), annot=True, cmap='coolwarm', center=0, ax=ax)
plt.title('Matrice de Corrélation')
plt.show()

# Distribution cible (pie chart)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
y_eda.value_counts().plot(kind='bar', ax=ax1)
ax1.set_title('Distribution Classes')
y_eda.value_counts().plot(kind='pie', ax=ax2, autopct='%1.1f%%')
ax2.set_title('Distribution % Classes')
plt.show()
```

---

**Rapportpréparé par** : EDA Approfondie Phase 2.1  
**Date** : 2026-05-27  
**Status** : ✅ **VALIDÉ**
