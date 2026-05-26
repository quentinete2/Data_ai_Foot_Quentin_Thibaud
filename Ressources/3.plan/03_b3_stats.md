# B3 — Endpoint `GET /api/stats`

## Objectif

Retourner les données agrégées nécessaires aux 2 sections du dashboard : le graphique des meilleures équipes (par pourcentage de victoires) et la métrique d'accuracy du modèle.

## Fichier cible

`CodeBase/backend/main.py`

## Structure de réponse cible

```json
{
  "top_teams_wins": [
    {"label": "Hungary", "value": 83.33},
    {"label": "Czechoslovakia", "value": 81.82},
    {"label": "Yugoslavia", "value": 81.25},
    {"label": "West Germany", "value": 79.49},
    {"label": "Norway", "value": 76.92},
    ...
  ],
  "top_teams_goals": [
    {"label": "Hungary", "value": 4.06},
    {"label": "Russia", "value": 3.17},
    {"label": "Norway", "value": 2.73},
    ...
  ],
  "metrics": {
    "accuracy": 0.6480
  }
}
```

## Source des données

Les stats viennent directement du bundle chargé au démarrage : `bundle["home_stats"]`.

**Pas besoin de lire le CSV** — les agrégats sont déjà calculés dans le bundle.

## Constante de métriques

```python
# Accuracy mesurée dans le notebook (cellule 15) — ne change pas (modèle figé)
MODEL_METRICS = {"accuracy": 0.6480}
```

## Implémentation

```python
MIN_MATCHES = 5  # filtre les équipes avec trop peu de matchs

@app.get("/api/stats")
def stats():
    top_teams_wins = []
    top_teams_goals = []

    if bundle is not None:
        home_stats = bundle["home_stats"]

        for team, s in home_stats.items():
            if s["total_matches"] >= MIN_MATCHES:
                win_pct = (s["wins"] / s["total_matches"]) * 100
                top_teams_wins.append({"label": team, "value": round(win_pct, 2)})
                top_teams_goals.append({"label": team, "value": round(s["avg_goals"], 3)})

        top_teams_wins = sorted(top_teams_wins, key=lambda x: x["value"], reverse=True)[:10]
        top_teams_goals = sorted(top_teams_goals, key=lambda x: x["value"], reverse=True)[:10]

    return {
        "top_teams_wins": top_teams_wins,
        "top_teams_goals": top_teams_goals,
        "metrics": MODEL_METRICS,
    }
```

## Valeurs attendues (top 5 wins — issues du notebook)

| Équipe | Win % |
|--------|-------|
| Hungary | 83.33 % |
| Czechoslovakia | 81.82 % |
| Yugoslavia | 81.25 % |
| West Germany | 79.49 % |
| Norway | 76.92 % |

## Validation

```bash
curl http://localhost:8000/api/stats
# → objet JSON avec top_teams_wins (10 items), top_teams_goals (10 items), metrics.accuracy
```

## Dépendances

- B1 doit être terminé (bundle chargé au démarrage)
- Indépendant de B2 — peut être développé en parallèle
- F3 (StatsChart) et F4 (Métriques) dépendent de B3
