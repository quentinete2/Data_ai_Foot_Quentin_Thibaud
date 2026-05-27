# Question Prédictive

## Énoncé clair du problème ML

**Comment prédire l'issue d'un match de Coupe du Monde (victoire domicile, match nul ou victoire visiteur) à partir des statistiques historiques de deux équipes ?**

---

## Cible (y)

| Propriété | Valeur |
|-----------|--------|
| **Nom de colonne** | `result` |
| **Type** | Catégorique (multiclasse : 3 classes) |
| **Classes** | `0` = home win, `1` = draw, `2` = away win |
| **Distribution** | **GRAVE déséquilibre** (56.33% / 16.83% / 26.84%) |
| **Ratio max/min** | 3.35 (> 25% = problématique) |

---

## Features X candidates

Toutes les features sont **agrégées par équipe** à partir de l'historique antérieur au match :

| # | Feature | Type | Signification | Exemple |
|---|---------|------|---------------|---------|
| 1 | `home_avg_goals` | float | Moyenne buts marqués par l'équipe domicile (historique) | 1.85 |
| 2 | `away_avg_goals` | float | Moyenne buts marqués par l'équipe visiteur (historique) | 1.42 |
| 3 | `goal_diff` | float | Différence buts marqués – buts encaissés pour domicile | +0.35 |
| 4 | `home_total_matches` | int | Nombre total de matchs de l'équipe domicile | 45 |
| 5 | `away_total_matches` | int | Nombre total de matchs de l'équipe visiteur | 42 |
| 6 | `home_wins` | int | Nombre de victoires de l'équipe domicile | 15 |
| 7 | `away_wins` | int | Nombre de victoires de l'équipe visiteur | 12 |
| 8 | `year` | int | Année du match (proxy pour force temporelle) | 2018 |
| 9 | `count_teams` | int | Nombre d'équipes au tournoi (8, 16, ou 32) | 32 |

**Justification** : ces 9 features capturent :
- **Attaque** : `home_avg_goals`, `away_avg_goals` — capacité à marquer
- **Défense** : `goal_diff` — qualité défensive relative
- **Expérience** : `total_matches`, `wins` — solidité du groupe
- **Contexte** : `year`, `count_teams` — tendances temporelles et format de tournoi

---

## Famille ML

**Classification multiclasse** (3 classes)

### Justification

- **Y est catégorique** (pas continu) → régression exclue
- **3 classes distinctes** (home win ≠ draw ≠ away win) → multiclasse requise
- **Utilité business** : prédire *quelle issue* (catégorique) plutôt qu'un score numérique

### Approche choisie

**RandomForestClassifier** (100 arbres, max_depth=10)

**Avantages** :
- Robuste aux features de types mixtes (int + float)
- Gère bien les interactions non-linéaires (ex : `home_avg_goals` × `goal_diff`)
- Interprétable (feature importance)
- Pas de normalisation requise
- Peu de tuning nécessaire

**Alternative rejetée** :
- **Logistic Regression** : trop simple, ne capture pas les interactions domicile/visiteur
- **SVM** : plus lent, nécessite normalisation, moins transparent
- **Neural Network** : overkill pour 9 features, trop difficile à expliquer aux stakeholders

---

## Métrique principale : Accuracy

| Métrique | Valeur (test set) | Justification |
|----------|-------------------|---------------|
| **Accuracy** | 64.80% | Métrique primaire — rapport prédictions correctes / total |
| **F1-score** | 0.63 (macro) | Important car 3 classes, déséquilibre modéré |
| **Precision/Recall** | ~0.62 / ~0.65 (par classe) | Pas plus d'importance que accuracy ici |

### Pourquoi accuracy doit être complétée ?

1. **Déséquilibre GRAVE détecté** : 56.33% / 16.83% / 26.84% (ratio 3.35)
   - L'accuracy seule est biaisée vers la classe majoritaire (Home Win)
   - Un modèle qui prédit "toujours Home Win" obtient 56% de baseline
   
2. **Metrics recommandées** :
   - **Primaire** : Accuracy (baseline 56% → objectif ≥ 65%)
   - **Secondaire** : **F1-score (macro)** — pénalise favoritisme classes minoritaires
   - **Tertaire** : Precision/Recall par classe (évaluer bias)

3. **Mitigation requise** :
   - `class_weight='balanced'` dans RandomForestClassifier
   - OU SMOTE (synthetic oversampling) en preprocessing

4. **Utilité** : En prédiction sportive, se tromper sur tout est grave
   - Faux négatif sur "Away Win" = mauvaise info au parieur
   - Modèle doit être équitable entre 3 classes

---

## 🔧 Résumé Exécutif Révisé (EDA Validé)

```
Je prédis l'issue d'un match de Coupe du Monde (home win / draw / away win)
à partir de 9 features (avg goals, total matches, wins, year, count_teams).

Famille ML              : Classification multiclasse (RandomForest)
Cible (y)              : result ∈ {0, 1, 2}
Distribution cible     : 56.33% / 16.83% / 26.84% [GRAVE DÉSÉQUILIBRE]
Features (X)           : 9 features avec corrélations 0.014–0.444
Metrics               : Accuracy + F1-score (macro) + Precision/Recall
Class balancing       : class_weight='balanced' REQUIS
Baseline              : 56.33% (toujours prédire home win)
Objectif              : ≥ 65% accuracy + F1 ≥ 0.50 (macro)
Lift attendu          : ~+16% vs baseline

⚠️ NOTE : L'EDA approfondie (étape 2.1) a révélé un déséquilibre bien
plus grave que prévu. Voir Ressources/3.plan/02_eda_approfondie.md pour details.
```

