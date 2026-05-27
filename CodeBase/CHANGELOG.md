# Changelog — Dashboard FIFA WC 2026

Format par entrée :
```
## [ID tâche] YYYY-MM-DD — Description courte
- Fichier(s) modifié(s) et ce qui a changé
- Comportement avant / après si pertinent
```

---

<!-- Les agents ajoutent leurs entrées ici, la plus récente en haut -->

## [Phase2.4] 2026-05-27 — API FastAPI minimale : /api/health + /api/predict + /api/stats ✅
- `CodeBase/etl/export_bundle.py` : script pour créer le bundle complet (modèle + stats d'équipes)
  - Charge modèle tuned de training_phase2_2.py
  - Calcule stats par équipe (home_stats, away_stats)
  - Exporte bundle vers backend/model.pkl (1.1 MB)
- `CodeBase/backend/main.py` : API complète (déjà implémentée Phase B1-B3)
  - ✅ `/api/health` : {status: "ok", model_loaded: true}
  - ✅ `/api/predict` : POST avec {home_team, away_team} → prédiction + probabilities + stats
  - ✅ `/api/stats` : GET → top_teams_wins, top_teams_goals, metrics.accuracy (0.648)
- ✅ Tests validés :
  - Bundle charge correctement au démarrage
  - /api/health répond immédiatement
  - /api/predict retourne prédictions avec confidence (ex: Germany 70.83%)
  - /api/stats retourne top teams et accuracy (64.8%)
- Stack vérifié : FastAPI + Pydantic + joblib + scikit-learn + CORS

## [Phase2.3] 2026-05-27 — Export du modèle et pinning des versions
- `CodeBase/backend/model.pkl` : modèle RandomForest (après tuning) exporté via joblib (1.1 MB, pas de git-lfs requis)
- `CodeBase/backend/requirements.txt` : versions pinnées pour compatibilité model.pkl
  - fastapi==0.115.0
  - uvicorn[standard]==0.30.6
  - pydantic==2.9.2
  - scikit-learn==1.5.2
  - joblib==1.4.2
  - pandas==2.2.3
- Modèle prêt pour chargement backend (main.py)

## [Phase2.2] 2026-05-27 — Baseline → Comparaison → Tuning : RandomForest wins (65.20% accuracy)
- `CodeBase/etl/training_phase2_2.py` : script complet implémentant 10 phases
  - Phase 1: Chargement 1248 matches
  - Phase 2: Feature engineering (9 features)
  - Phase 3: Train/Test split 80/20 stratifié (train: 998, test: 250)
  - Phase 4-6: Baseline LogisticRegression (CV 57.52% acc / 58.80% test) vs RandomForest (CV 60.82% acc / 64.00% test) vs GradientBoosting (CV 59.52% acc / 62.80% test)
  - Phase 7: GridSearchCV tuning RandomForest (36 combinaisons, 180 fits)
  - Phase 8: Évaluation finale test set : 65.20% accuracy, 0.5417 F1-score (macro)
  - Phase 9: Tableau récapitulatif comparatif
  - Phase 10: Export model_final.pkl
- Hyperparamètres finaux : n_estimators=100, max_depth=8, min_samples_split=10, class_weight='balanced'
- Amélioration vs Baseline : +6.40% accuracy (+10.9% relatif), +3.1% F1-score
- Confusion matrix: Home 77% recall, Draw 19% recall, Away 70% recall
- Avant : LR 58.80% / Après : RF-tuned 65.20%
- Issues détectées : Draw prédiction faible (minoritaire 16%) → recommandation SMOTE future
- `Ressources/3.plan/03_training_phase2_2.md` : rapport détaillé avec findings et next steps

## [D1] 2026-05-26 — Déploiement Docker (backend + frontend + compose)
- `CodeBase/backend/Dockerfile` : image python:3.11-slim, installe requirements, expose 8000
- `CodeBase/backend/.dockerignore` : exclut __pycache__, .venv, node_modules
- `CodeBase/frontend/Dockerfile` : build multi-stage node:20-alpine → nginx:alpine, expose 80
- `CodeBase/frontend/.dockerignore` : exclut node_modules, dist
- `CodeBase/docker-compose.yml` : service backend (8000) + frontend (80) avec depends_on
- CORS `http://localhost` déjà présent dans main.py (D1-d)

## [F1-F4] 2026-05-26 — Implémentation complète du frontend
- `CodeBase/frontend/src/api.ts` : types TS alignés sur le backend (MatchInput, PredictResponse, TeamStats, StatItem, StatsResponse) + signatures predire/getStats mises à jour
- `CodeBase/frontend/src/PredictionForm.tsx` : formulaire 2 champs texte (home_team/away_team), affichage résultat (prediction + confidence + 3 probabilités en grille)
- `CodeBase/frontend/src/StatsChart.tsx` : nouveau composant BarChart Recharts (top_teams_wins, ResponsiveContainer, labels inclinés)
- `CodeBase/frontend/src/App.tsx` : query activée (enabled:true), StatsChart intégré, MetricCard avec accuracy 64.8 %
- Avant : TODOs partout, useQuery désactivé / Après : dashboard complet fonctionnel, npm run typecheck → 0 erreur

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
