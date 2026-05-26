# B1 — Modèle Pydantic `MatchInput`

## Objectif

Remplacer le `pass` dans la classe d'entrée par les 2 champs qui correspondent exactement à l'interface du nouveau modèle : `home_team` et `away_team` (noms d'équipes en clair). Le vecteur de 9 features est construit **côté backend** à partir des stats stockées dans le bundle.

## Fichier cible

`CodeBase/backend/main.py`

## Code à écrire

```python
class MatchInput(BaseModel):
    home_team: str   # ex: "France", "Brazil"
    away_team: str   # ex: "Mexico", "Germany"
```

## Labels de résultat (à ajouter comme constante)

```python
RESULT_LABELS = {
    0: "home_win",
    1: "draw",
    2: "away_win",
}
```

## Chargement du bundle au démarrage

```python
import joblib
from pathlib import Path

bundle = None
try:
    bundle = joblib.load(Path(__file__).parent / "model.pkl")
except FileNotFoundError:
    pass

# Accès aux composants du bundle :
# bundle["model"]              → RandomForestClassifier
# bundle["home_stats"]         → dict {team: {avg_goals, total_matches, wins}}
# bundle["away_stats"]         → dict {team: {avg_goals, total_matches, wins}}
# bundle["median_year"]        → float
# bundle["median_count_teams"] → float
```

## Pourquoi ces types

- `str` pour les noms d'équipes — le backend fait le lookup dans les dicts de stats
- Pydantic valide que les deux champs sont des strings non-vides
- L'équipe peut être inconnue (pas dans les 84) → stats ramenées à 0, pas d'erreur

## Validation

```bash
# Le endpoint doit accepter sans erreur 422 :
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team":"France","away_team":"Mexico"}'
```

## Dépendances

- Aucune — peut être fait avant même d'avoir `model.pkl`
- B2 dépend de B1
