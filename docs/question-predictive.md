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
| **Distribution** | légèrement déséquilibrée (36% / 24% / 40%) |

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

### Pourquoi accuracy d'abord ?

1. **Business clarity** : « le modèle prédit correctement 64.8% des résultats » = message simple
2. **Déséquilibre tolérable** : pas grave (36% / 24% / 40%), accuracy = bon proxy
3. **Utilité** : en prédiction sportive, se tromper sur home/draw/away a la même gravité
4. **Baseline** : prédir always home win = 36% accuracy → 64.8% = gain +78%

---

## Résumé exécutif

```
Je prédis l'issue d'un match de Coupe du Monde (home win / draw / away win)
à partir de 9 features (avg goals, total matches, wins, year, count_teams).

Famille ML  : Classification multiclasse (RandomForest)
Métrique    : Accuracy 64.80% (F1 0.63 macro)
Baseline    : 36% (toujours prédire home win)
Lift        : +78% par rapport à baseline
```

