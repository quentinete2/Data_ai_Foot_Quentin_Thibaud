# B3 — Endpoint `GET /api/stats`

## Objectif

Retourner les données agrégées nécessaires aux 2 sections du dashboard : le graphique des meilleures équipes et les métriques du modèle (MAE, RMSE).

## Fichier cible

`CodeBase/backend/main.py` — lignes 46–50

## Structure de réponse cible

```json
{
  "top_teams": [
    {"label": "Brazil", "value": 5.1},
    {"label": "Germany", "value": 4.8},
    ...
  ],
  "stage_distribution": {
    "1": 124, "2": 64, "3": 32, "4": 16, "5": 8, "6": 4
  },
  "metrics": {
    "mae": 0.82,
    "rmse": 1.05,
    "r2": 0.61
  }
}
```

## Approche : données en dur vs. CSV

**Option recommandée pour ce cours : données partiellement en dur**

Les métriques MAE/RMSE sont calculées dans le notebook (cellule 15). Les noter et les mettre en dur dans `main.py` — c'est correct car elles ne changent pas (le modèle ne se ré-entraîne pas).

Pour `top_teams`, charger le CSV `matches.csv` au démarrage et calculer les agrégats une fois.

## Implémentation

```python
import pandas as pd
import numpy as np
from pathlib import Path

# Charger les données au démarrage (une seule fois)
DATA_PATH = Path(__file__).parents[2] / "Ressources" / "Data"
matches_df: pd.DataFrame | None = None
try:
    matches_df = pd.read_csv(DATA_PATH / "matches.csv")
except FileNotFoundError:
    pass

# Métriques du modèle (issues du notebook, cellule 15)
MODEL_METRICS = {"mae": 0.82, "rmse": 1.05, "r2": 0.61}  # à mettre à jour avec vos valeurs réelles

@app.get("/api/stats")
def stats():
    top_teams = []
    stage_distribution = {}

    if matches_df is not None:
        # Top équipes par nombre de victoires
        wins = matches_df[matches_df["resultat"] == "V"].groupby("equipe")["resultat"].count()
        top = wins.sort_values(ascending=False).head(10)
        top_teams = [{"label": team, "value": int(count)} for team, count in top.items()]

        # Distribution des stades atteints
        if "stade_atteint" in matches_df.columns:
            dist = matches_df["stade_atteint"].value_counts().sort_index()
            stage_distribution = {str(k): int(v) for k, v in dist.items()}

    return {
        "top_teams": top_teams,
        "stage_distribution": stage_distribution,
        "metrics": MODEL_METRICS,
    }
```

## Note sur les noms de colonnes

Les colonnes exactes de `matches.csv` sont à vérifier. Les noms dans le notebook (cellule 10-11) font référence. Adapter le code si besoin.

## Validation

```bash
curl http://localhost:8000/api/stats
# → objet JSON avec top_teams, stage_distribution, metrics
```

## Dépendances

- Indépendant de B1/B2 — peut être développé en parallèle
- F3 (StatsChart) et F4 (Métriques) dépendent de B3
