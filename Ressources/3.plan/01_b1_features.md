# B1 — Modèle Pydantic `Features`

## Objectif

Remplacer le `pass` dans la classe `Features` par les 8 champs qui correspondent exactement aux features utilisées à l'entraînement (même nom, même type, même ordre).

## Fichier cible

`CodeBase/backend/main.py` — lignes 24–27

## Code à écrire

```python
class Features(BaseModel):
    nb_participations: int
    taux_victoire_historique: float
    buts_marques_moy: float
    buts_encaisses_moy: float
    diff_buts_moy: float
    meilleur_stade_atteint: int
    stade_dernier_tournoi: int
    est_hote: int  # 0 ou 1
```

## Pourquoi ces types

- `int` pour les compteurs entiers (`nb_participations`, `meilleur_stade_atteint`, `stade_dernier_tournoi`, `est_hote`)
- `float` pour les moyennes et taux (sklearn accepte float64, compatible Python float)
- L'ordre dans la classe détermine l'ordre dans le tableau numpy → doit correspondre à l'entraînement

## Validation

```bash
# Tester manuellement après démarrage du backend
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"nb_participations":22,"taux_victoire_historique":0.65,"buts_marques_moy":1.8,"buts_encaisses_moy":0.9,"diff_buts_moy":0.9,"meilleur_stade_atteint":6,"stade_dernier_tournoi":4,"est_hote":0}'
# → doit retourner sans erreur de validation Pydantic (422)
```

## Dépendances

- Aucune — peut être fait avant même d'avoir `model.pkl`
- B2 dépend de B1
