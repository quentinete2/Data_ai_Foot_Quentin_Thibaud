# Changelog — Dashboard FIFA WC 2026

Format par entrée :
```
## [ID tâche] YYYY-MM-DD — Description courte
- Fichier(s) modifié(s) et ce qui a changé
- Comportement avant / après si pertinent
```

---

<!-- Les agents ajoutent leurs entrées ici, la plus récente en haut -->

## [B3] 2026-05-26 — Implémentation GET /api/stats
- `CodeBase/backend/main.py` : endpoint /api/stats implémenté
- Retourne top_teams_wins (10 équipes, % victoires), top_teams_goals (10 équipes, moy. buts) et metrics.accuracy
- Données issues du bundle (home_stats), filtre MIN_MATCHES=5, constante MODEL_METRICS = {"accuracy": 0.6480}
- Avant : {"todo": "completer /api/stats"} / Après : JSON complet conforme au plan B3

## [B2] 2026-05-26 — Implémentation POST /api/predict
- `CodeBase/backend/main.py` : endpoint /api/predict implémenté
- Reçoit {home_team, away_team}, construit le vecteur de 9 features, appelle model.predict + predict_proba
- Retourne prediction (label), confidence, probabilities (3 classes), home_stats, away_stats
- Avant : {"prediction": null, "todo": "completer predict()"} / Après : réponse JSON complète (ex: "Victoire France" 48.29%)

## [B1] 2026-05-26 — Modèle Pydantic MatchInput + chargement bundle
- `CodeBase/backend/main.py` : classe Features remplacée par MatchInput (home_team: str, away_team: str)
- Chargement du bundle (model, home_stats, away_stats, median_year, median_count_teams) via try/except FileNotFoundError
- Ajout de RESULT_LABELS, MODEL_METRICS, MIN_MATCHES, get_team_stats()
- `CodeBase/etl/generate_model.py` : script créé pour entraîner et exporter model.pkl depuis le notebook
- Avant : class Features(BaseModel): pass / Après : MatchInput valide, bundle chargé au démarrage
