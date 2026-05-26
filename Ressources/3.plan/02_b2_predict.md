# B2 — Endpoint `POST /api/predict`

## Objectif

Implémenter la logique de prédiction dans `predict()` : récupérer les stats des deux équipes dans le bundle, construire le vecteur de 9 features, appeler `model.predict()` et `model.predict_proba()`, retourner la prédiction + confiance + probabilités + stats des deux équipes.

## Fichier cible

`CodeBase/backend/main.py`

## Logique de lookup des stats

```python
def get_team_stats(stats_dict: dict, team: str) -> dict:
    """Retourne les stats d'une équipe, ou des stats à 0 si inconnue."""
    return stats_dict.get(team, {"avg_goals": 0, "total_matches": 0, "wins": 0})
```

## Logique de l'endpoint

```python
from fastapi import HTTPException
import numpy as np

@app.post("/api/predict")
def predict(match: MatchInput):
    if bundle is None:
        raise HTTPException(status_code=503, detail="model.pkl manquant")

    model = bundle["model"]
    home_stats = bundle["home_stats"]
    away_stats = bundle["away_stats"]
    median_year = bundle["median_year"]
    median_count_teams = bundle["median_count_teams"]

    home_stat = get_team_stats(home_stats, match.home_team)
    away_stat = get_team_stats(away_stats, match.away_team)

    features = np.array([[
        home_stat["avg_goals"],
        away_stat["avg_goals"],
        home_stat["avg_goals"] - away_stat["avg_goals"],  # goal_diff
        home_stat["total_matches"],
        away_stat["total_matches"],
        home_stat["wins"],
        away_stat["wins"],
        median_year,
        median_count_teams,
    ]])

    prediction_class = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0]

    label = (
        f"Victoire {match.home_team}" if prediction_class == 0
        else "Match Nul" if prediction_class == 1
        else f"Victoire {match.away_team}"
    )

    return {
        "prediction": label,
        "confidence": float(probabilities[prediction_class]),
        "probabilities": {
            "home_win": float(probabilities[0]),
            "draw": float(probabilities[1]),
            "away_win": float(probabilities[2]),
        },
        "home_stats": home_stat,
        "away_stats": away_stat,
    }
```

## Ordre des features (doit correspondre à l'entraînement)

```python
features_for_model = [
    'home_avg_goals',    # home_stat["avg_goals"]
    'away_avg_goals',    # away_stat["avg_goals"]
    'goal_diff',         # home - away avg_goals
    'home_total_matches',
    'away_total_matches',
    'home_wins',
    'away_wins',
    'year',              # median_year
    'count_teams',       # median_count_teams
]
```

## Points importants

- `raise HTTPException(503)` si le bundle est absent
- `get_team_stats` retourne des stats à 0 pour les équipes non connues (pas d'erreur 404)
- `float()` sur les valeurs numpy pour la sérialisation JSON (numpy float64 n'est pas JSON-serializable nativement)
- Les probabilités somment à 1.0 (garantie de `predict_proba`)

## Validation

```bash
# Exemple France vs Mexico — réponse attendue similaire au notebook :
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team":"France","away_team":"Mexico"}'

# Réponse attendue :
# {
#   "prediction": "Victoire France",
#   "confidence": 0.4829,
#   "probabilities": {"home_win": 0.4829, "draw": 0.3160, "away_win": 0.2012},
#   "home_stats": {...},
#   "away_stats": {...}
# }
```

## Validation Playwright (via browser_evaluate)

```javascript
fetch('http://localhost:8000/api/predict', {
  method: 'POST',
  headers: {'Content-Type':'application/json'},
  body: JSON.stringify({home_team: 'France', away_team: 'Mexico'})
}).then(r=>r.json()).then(console.log)
```

## Dépendances

- B1 doit être terminé (`MatchInput` défini, bundle chargé au startup)
- `model.pkl` (bundle) doit exister dans `backend/`
