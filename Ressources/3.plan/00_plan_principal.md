# Plan principal — Dashboard FIFA WC 2026

## Vue d'ensemble

Le squelette est en place. Il reste à connecter le modèle ML au backend et brancher le frontend dessus. Tout est du remplissage de TODOs ciblés — aucune réécriture globale.

## Pré-requis

- [ ] `model.pkl` exporté depuis le notebook (`joblib.dump(pipeline, "backend/model.pkl")`)
- [ ] `pip install -r requirements.txt` dans `CodeBase/backend/`
- [ ] `npm install` dans `CodeBase/frontend/`

---

## Ordre d'exécution recommandé

```
[B1] Features Pydantic  →  [B2] /api/predict  →  [B3] /api/stats
                                                          ↓
[F1] Types api.ts       →  [F2] PredictionForm  →  [F3] StatsChart + [F4] Métriques
```

**Règle** : finir le backend avant d'activer le frontend — le frontend dépend des réponses réelles.

---

## Backend (`CodeBase/backend/main.py`)

| ID | Sous-tâche | Fichier | Complexité |
|----|-----------|---------|-----------|
| B1 | Définir le modèle Pydantic `Features` (8 champs) | `main.py:24-27` | Faible |
| B2 | Implémenter `POST /api/predict` | `main.py:35-43` | Faible |
| B3 | Implémenter `GET /api/stats` | `main.py:46-50` | Moyenne |

Détails : voir `01_b1_features.md`, `02_b2_predict.md`, `03_b3_stats.md`

---

## Frontend (`CodeBase/frontend/src/`)

| ID | Sous-tâche | Fichier | Complexité |
|----|-----------|---------|-----------|
| F1 | Aligner les types TypeScript avec les réponses réelles | `api.ts` | Faible |
| F2 | Champs du formulaire de prédiction | `PredictionForm.tsx` | Faible |
| F3 | Composant `StatsChart` (Recharts BarChart) | nouveau `StatsChart.tsx` | Moyenne |
| F4 | Section métriques modèle (MAE/RMSE) | `App.tsx:29-30` | Faible |

Détails : voir `04_f1_types.md`, `05_f2_form.md`, `06_f3_chart.md`, `07_f4_metriques.md`

---

## Déploiement Docker (après validation locale)

| ID | Sous-tâche | Fichier | Complexité |
|----|-----------|---------|-----------|
| D1-a | `Dockerfile` backend | `CodeBase/backend/Dockerfile` | Faible |
| D1-b | `Dockerfile` frontend (multi-stage) | `CodeBase/frontend/Dockerfile` | Faible |
| D1-c | `docker-compose.yml` | `CodeBase/docker-compose.yml` | Faible |
| D1-d | CORS : ajouter `http://localhost` | `main.py` | Faible |

Détails : voir `08_deploiement_docker.md`

---

## Critères de validation finale

- `GET /api/health` → `{"status": "ok", "model_loaded": true}`
- `POST /api/predict` avec les 8 features → retourne `predicted_stage` (float) + `stage_label` (string)
- `GET /api/stats` → objet avec `top_teams`, `stage_distribution`, `metrics`
- Dashboard : graphique visible, formulaire soumettable, métriques affichées
- `npm run typecheck` → 0 erreur
