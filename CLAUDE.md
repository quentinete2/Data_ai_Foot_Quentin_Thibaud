# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FIFA World Cup 2026 prediction dashboard — a B3 course project. An ML model trained on historical World Cup data (1930–2022) is served via a FastAPI backend and consumed by a React frontend. The notebook trains and exports `model.pkl`; the app loads it, never retrains it.

## Repository Layout

```
BigData/
├── CodeBase/           # The application (backend + frontend + notebook)
│   ├── backend/        # FastAPI, loads model.pkl via joblib
│   ├── frontend/       # React 18 + Vite + TypeScript SPA
│   └── etl/            # Jupyter notebook (trains model → exports model.pkl)
└── Ressources/Data/    # Raw CSVs: matches.csv (1248 rows), tournaments.csv (30 rows)
```

## Running the App

**Backend** (terminal 1 — from `CodeBase/backend/`):
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# model.pkl must be present (export from notebook: joblib.dump(pipeline, "model.pkl"))
python main.py          # http://localhost:8000  (test: GET /api/health)
```

**Frontend** (terminal 2 — from `CodeBase/frontend/`):
```bash
npm install
npm run dev             # http://localhost:5173
npm run typecheck       # type-check only
npm run build           # production build (outputs dist/)
```

**Docker deployment** (from `CodeBase/`):
```bash
docker-compose up --build   # démarre backend (port 8000) + frontend Nginx (port 80)
```
Pré-requis : `model.pkl` présent dans `backend/`. Voir `Ressources/3.plan/08_deploiement_docker.md`.

## ML Pipeline

`CodeBase/etl/Data_ia_foot.ipynb` trains the model end-to-end:
- **Data**: loads `matches.csv` + `tournaments.csv` from GitHub (mirrors `Ressources/Data/`)
- **Task**: **Classification** — predict match result: 0 = home win, 1 = draw, 2 = away win
- **Features** (9, per match): `home_avg_goals`, `away_avg_goals`, `goal_diff`, `home_total_matches`, `away_total_matches`, `home_wins`, `away_wins`, `year`, `count_teams`
- **Random split**: `train_test_split(test_size=0.2, random_state=42)` — 998 train / 250 test
- **Model**: `RandomForestClassifier(n_estimators=100, max_depth=10)` — no sklearn Pipeline
- **Accuracy**: 64.80 % on test set
- **Export**: `joblib.dump(bundle, "backend/model.pkl")` where bundle = `{model, home_stats, away_stats, median_year, median_count_teams}`

The `POST /api/predict` endpoint receives `{home_team: str, away_team: str}` — feature construction (stat lookup) happens in the backend, not in the client.

## Architecture

- `backend/main.py`: one file, CORS allows `localhost:5173`, loads `model.pkl` at startup; `/api/predict` and `/api/stats` are the main endpoints (TODOs remain)
- `frontend/src/api.ts`: all API calls centralized here; use `useQuery`/`useMutation` from React Query — no bare `fetch` in components
- `frontend/src/App.tsx`: three dashboard sections (stats, prediction form, model performance)
- `frontend/src/PredictionForm.tsx`: controlled form with React Query mutation, 2 text fields (home_team / away_team), displays prediction + probabilities
- Import alias: `@/` → `src/`; shadcn components: `npx shadcn@latest add <component>`; charts always inside `<ResponsiveContainer>`

## Conventions (from `CodeBase/CLAUDE.md`)

- Server data → **React Query**; local state → `useState`; no global state library
- Surgical edits only; don't rewrite working files wholesale
- Never modify an endpoint contract without flagging it
- Common errors: CORS → check ports match; blank chart → missing `<ResponsiveContainer>` or empty `/api/stats`; model crash → bundle keys missing or team name not found in stats dict

## Development Agent Workflow

### 0. Lecture obligatoire avant de commencer

Lire `Ressources/3.plan/00_plan_principal.md` en premier. Ce fichier contient l'ordre d'exécution et les critères de validation finale.

### 1. Ordre d'exécution strict

```
B1 → B2 → B3   (backend complet en premier)
          ↓
F1 → F2 → F3 → F4
```

Ne jamais commencer F1 avant que B3 soit validé via Playwright.

### 2. Boucle par tâche (répéter pour chaque ID)

```
LIRE     Ressources/3.plan/<fichier_plan>.md
           ↓
CODER    avec le bon skill (voir ci-dessous)
           ↓
LANCER   backend + frontend en arrière-plan
           ↓
TESTER   via Playwright MCP
           ↓
CORRIGER si erreur → retour à TESTER
           ↓
DOCUMENTER dans CodeBase/CHANGELOG.md (entrée en haut du fichier)
           ↓
COMMITER les fichiers modifiés (git add + git commit)
           ↓
PASSER   à la tâche suivante
```

Fichiers plan par tâche :
| Tâche | Fichier plan |
|-------|-------------|
| B1 | `Ressources/3.plan/01_b1_features.md` |
| B2 | `Ressources/3.plan/02_b2_predict.md` |
| B3 | `Ressources/3.plan/03_b3_stats.md` |
| F1 | `Ressources/3.plan/04_f1_types.md` |
| F2 | `Ressources/3.plan/05_f2_form.md` |
| F3 | `Ressources/3.plan/06_f3_chart.md` |
| F4 | `Ressources/3.plan/07_f4_metriques.md` |

### 3. Skills à utiliser

- **Tâches B1–B3 (backend FastAPI)** → invoquer `Skill("fastapi-python")` avant de coder
- **Tâches F1–F4 (frontend React/TS)** → appliquer les patterns `CodeBase/CLAUDE.md` ; pour composants complexes invoquer `Skill("web-artifacts-builder")`

### 4. Démarrage des serveurs

```powershell
# Backend (depuis la racine du repo)
Start-Process python -ArgumentList "CodeBase/backend/main.py" -WindowStyle Hidden
# Frontend
Start-Process npm -ArgumentList "--prefix","CodeBase/frontend","run","dev" -WindowStyle Hidden
```

Attendre ~3s puis vérifier que `http://localhost:8000/api/health` répond avant de lancer Playwright.

### 5. Tests Playwright MCP — protocole

Après chaque tâche, exécuter dans cet ordre :

**Backend (toutes les tâches B)** :
```
browser_navigate → http://localhost:8000/api/health
  → vérifier {"status":"ok","model_loaded":true}
browser_navigate → http://localhost:8000/api/stats   (après B3)
  → vérifier top_teams_wins, top_teams_goals, metrics.accuracy présents
```

Pour `/api/predict`, utiliser `browser_evaluate` pour envoyer un POST :
```javascript
fetch('http://localhost:8000/api/predict', {
  method: 'POST',
  headers: {'Content-Type':'application/json'},
  body: JSON.stringify({home_team: 'France', away_team: 'Mexico'})
}).then(r=>r.json()).then(console.log)
```

**Frontend (tâches F)** :
```
browser_navigate → http://localhost:5173
browser_screenshot → vérifier rendu visuel
browser_console_messages → vérifier absence d'erreurs JS
browser_fill + browser_click → tester soumission du formulaire
browser_screenshot → vérifier résultat de prédiction affiché
```

**Si erreur détectée** : lire les messages console (`browser_console_messages`), corriger le code, redémarrer le serveur concerné, re-tester. Ne pas passer à la tâche suivante tant que Playwright ne confirme pas le bon fonctionnement.

### 6. Documenter et commiter (après validation Playwright)

**Étape 1 — CHANGELOG** : ajouter une entrée en haut de `CodeBase/CHANGELOG.md` :
```
## [B2] 2026-05-26 — Implémentation POST /api/predict
- `CodeBase/backend/main.py` : endpoint /api/predict implémenté, retourne predicted_stage + stage_label
- Avant : 501 Not Implemented / Après : réponse JSON correcte avec les 8 features
```

**Étape 2 — Git commit** : stager uniquement les fichiers modifiés par la tâche + le CHANGELOG :
```bash
git add CodeBase/backend/main.py CodeBase/CHANGELOG.md
git commit -m "[B2] Implémenter POST /api/predict"
```

Règles du commit :
- Préfixer avec l'ID de la tâche : `[B1]`, `[F3]`, etc.
- Ne stager que les fichiers touchés par la tâche en cours (pas `git add .`)
- Un commit par tâche validée, pas avant

### 7. Checklist de validation finale

- `GET /api/health` → `{"status": "ok", "model_loaded": true}`
- `POST /api/predict` `{home_team, away_team}` → `{prediction, confidence, probabilities, home_stats, away_stats}`
- `GET /api/stats` → objet avec `top_teams_wins`, `top_teams_goals`, `metrics.accuracy`
- Dashboard charge dans le navigateur, formulaire soumettable, graphique visible, accuracy affichée
- `npm run typecheck` → 0 erreurs
