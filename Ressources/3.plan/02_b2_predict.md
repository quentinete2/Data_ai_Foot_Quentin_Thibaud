# B2 — Endpoint `POST /api/predict`

## Objectif

Implémenter la logique de prédiction dans `predict()` : construire le vecteur de features dans le bon ordre, appeler `model.predict()`, retourner le stage prédit + son label texte.

## Fichier cible

`CodeBase/backend/main.py` — lignes 35–43

## Labels des stades

```python
STAGE_LABELS = {
    1: "Phase de groupes",
    2: "Huitièmes de finale",
    3: "Quarts de finale",
    4: "Demi-finales",
    5: "Finale",
    6: "Vainqueur",
}
```

À ajouter en haut du fichier (après les imports, avant la classe `Features`).

## Logique de l'endpoint

```python
from fastapi import HTTPException

@app.post("/api/predict")
def predict(features: Features):
    if model is None:
        raise HTTPException(status_code=503, detail="model.pkl manquant")

    x = [[
        features.nb_participations,
        features.taux_victoire_historique,
        features.buts_marques_moy,
        features.buts_encaisses_moy,
        features.diff_buts_moy,
        features.meilleur_stade_atteint,
        features.stade_dernier_tournoi,
        features.est_hote,
    ]]
    pred = float(model.predict(x)[0])
    stage_int = max(1, min(6, round(pred)))
    return {
        "predicted_stage": pred,
        "stage_label": STAGE_LABELS.get(stage_int, "Inconnu"),
    }
```

## Points importants

- `raise HTTPException(503)` au lieu de retourner un dict d'erreur (HTTP sémantique correct, le frontend peut détecter l'erreur proprement)
- `round(pred)` + clamp `[1, 6]` pour afficher un label cohérent même si le modèle prédit hors-range
- L'ordre des features dans `x` doit être identique à l'ordre d'entraînement dans le notebook (cell 12)

## Validation

```bash
# Réponse attendue :
# {"predicted_stage": 4.8, "stage_label": "Demi-finales"}
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"nb_participations":22,"taux_victoire_historique":0.65,"buts_marques_moy":1.8,"buts_encaisses_moy":0.9,"diff_buts_moy":0.9,"meilleur_stade_atteint":6,"stade_dernier_tournoi":4,"est_hote":0}'
```

## Dépendances

- B1 doit être terminé (classe `Features` définie)
- `model.pkl` doit exister dans `backend/`
