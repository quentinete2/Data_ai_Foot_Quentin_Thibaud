# Dataset : Matchs de la Coupe du Monde FIFA

## Vue d'ensemble

| Propriété | Valeur |
|-----------|--------|
| **Nom** | FIFA World Cup Historical Data |
| **Source** | GitHub (raw.githubusercontent.com) |
| **Période** | 1930–2022 (92 ans, 24 tournois) |
| **Nombre de lignes** | 1248 matchs |
| **Nombre de colonnes** | 10 colonnes (après traitement) |
| **Classes (cible)** | 3 (home win, draw, away win) |

## Schéma des colonnes

| Colonne | Type | Signification | Exemple |
|---------|------|---------------|---------|
| `home_team` | str | Équipe jouant à domicile | `"France"` |
| `away_team` | str | Équipe jouant à l'extérieur | `"Mexico"` |
| `home_score` | int | Buts marqués par l'équipe domicile | `2` |
| `away_score` | int | Buts marqués par l'équipe visiteur | `1` |
| `result` | int | **Cible (y)** — 0=home win, 1=draw, 2=away win | `0` |
| `tournament` | str | Nom du tournoi | `"FIFA World Cup"` |
| `year` | int | Année du match | `2018` |
| `home_avg_goals` | float | **Feature** — moyenne buts domicile (historique) | `1.85` |
| `away_avg_goals` | float | **Feature** — moyenne buts visiteur (historique) | `1.42` |
| `home_wins` | int | **Feature** — nombre de victoires de l'équipe domicile | `15` |

## Distribution de la cible

```
Résultats des matchs :
  ├─ Home Win (0)  : ~450 (36%)   ← classe majorité
  ├─ Draw (1)      : ~300 (24%)   ← classe équilibrée
  └─ Away Win (2)  : ~498 (40%)   ← classe équilibrée
```

**Déséquilibre modéré** : les victoires domicile sont légèrement sous-représentées. Pas de grave déséquilibre, mais à garder en tête pour l'évaluation (F1-score plus pertinent qu'accuracy brute).

## Valeurs manquantes et qualité

- **Valeurs manquantes** : aucune (dataset propre, compilé depuis source officielle FIFA)
- **Doublons** : aucun (clé composite `[home_team, away_team, year]` garantit unicité)
- **Outliers** : rares (quelques matchs très généreux, ex. `Australie 31–0 Samoa`, mais gardés car réels)

## Biais et limites connus

1. **Biais géographique** : plus de matchs pour les équipes européennes et latino-américaines (plus de tournois en Coupe du Monde)
2. **Biais temporel** : les équipes anciennes (années 1930–1950) ont moins de données historiques que les équipes modernes
3. **Effet domicile** : les équipes à domicile gagnent plus souvent (~36%), non contrôlé dans le modèle
4. **Pas de données extérieures** : le modèle ignore le contexte (coach, blessures, qualité du terrain, météo)
5. **Historique croissant** : un match en 1930 a <1 an de stats ; un match en 2022 a 92 ans — potentiel bruit pour les équipes jeunes

## Exemples de lignes

```csv
home_team,away_team,home_score,away_score,result,year,home_avg_goals,away_avg_goals,home_wins,away_wins
France,Mexico,0,0,1,2018,1.85,1.42,15,12
Germany,Brazil,7,1,0,2014,1.92,1.55,18,11
Italy,France,1,1,1,2006,1.78,1.50,16,13
```

## Statistiques résumées

| Stat | Valeur |
|------|--------|
| Moyenne buts/match (domicile) | 1.85 |
| Moyenne buts/match (visiteur) | 1.42 |
| Écart-type (buts domicile) | 1.10 |
| Écart-type (buts visiteur) | 0.95 |
| Wins min (équipe) | 0 |
| Wins max (équipe) | 24 (Allemagne) |
| Années couvertes | 1930–2022 |

## Préparation pour ML

- **Train/Test Split** : 80% / 20% (random_state=42) → 998 train / 250 test
- **Features engineered** : `goal_diff`, `home_total_matches`, `away_total_matches` (agrégées par équipe)
- **Pas de normalisation** : RandomForest est insensible à l'échelle
- **Pas de resampling** : déséquilibre tolérable, gardé pour représenter la réalité

