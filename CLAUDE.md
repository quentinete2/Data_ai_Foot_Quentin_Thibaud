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

**Deployment**: `npm run build` in `frontend/`, then uncomment the `StaticFiles` block in `backend/main.py` → single FastAPI app.

## ML Pipeline

`CodeBase/etl/Data_ia_foot.ipynb` trains the model end-to-end:
- **Data**: loads `matches.csv` + `tournaments.csv` from GitHub (mirrors `Ressources/Data/`)
- **Target** `stade_atteint`: stage reached, 1 (group) → 6 (winner)
- **Features** (per team, per tournament): `nb_participations`, `taux_victoire_historique`, `buts_marques_moy`, `buts_encaisses_moy`, `diff_buts_moy`, `meilleur_stade_atteint`, `stade_dernier_tournoi`, `est_hote`
- **Temporal split**: train 1930–2018, test 2022 Qatar; 2026 predictions include host flag for USA/Canada/Mexico
- **Models**: Random Forest Regressor + Gradient Boosting Regressor, both in sklearn `Pipeline` (imputer → scaler → model)
- **Export**: `joblib.dump(pipeline, "backend/model.pkl")`

The Pydantic `Features` model in `backend/main.py` must match these 8 feature names exactly — order/types must match training.

## Architecture

- `backend/main.py`: one file, CORS allows `localhost:5173`, loads `model.pkl` at startup; `/api/predict` and `/api/stats` are the main endpoints (TODOs remain)
- `frontend/src/api.ts`: all API calls centralized here; use `useQuery`/`useMutation` from React Query — no bare `fetch` in components
- `frontend/src/App.tsx`: three dashboard sections (stats, prediction form, model performance)
- `frontend/src/PredictionForm.tsx`: controlled form with React Query mutation, one field per feature
- Import alias: `@/` → `src/`; shadcn components: `npx shadcn@latest add <component>`; charts always inside `<ResponsiveContainer>`

## Conventions (from `CodeBase/CLAUDE.md`)

- Server data → **React Query**; local state → `useState`; no global state library
- Surgical edits only; don't rewrite working files wholesale
- Never modify an endpoint contract without flagging it
- Common errors: CORS → check ports match; blank chart → missing `<ResponsiveContainer>` or empty `/api/stats`; model crash → feature order/types mismatch with training
