# FIFA World Cup 2026 Prediction Dashboard

> **Predict match outcomes** using historical World Cup data and machine learning. A fullstack application combining React frontend, FastAPI backend, and a pre-trained RandomForest model.

---

## 📋 Project Overview

**What**: A web dashboard that predicts the outcome of FIFA World Cup matches (home win / draw / away win) using 92 years of historical data (1930–2022, 1248 matches).

**For whom**: Football enthusiasts, analysts, and educators exploring ML-driven predictions in sports.

**Dataset**: FIFA World Cup historical data
  - **Source**: GitHub (publicly available)
  - **Size**: 1248 matches × 10 features
  - **Period**: 1930–2022 (24 tournaments)
  - **Classes**: 3 (home win: 36%, draw: 24%, away win: 40%)

**ML Task**: Multiclass classification (RandomForestClassifier, 100 trees)  
**Accuracy**: 64.80% on test set (baseline: 36% → **+78% lift**)

---

## 🛠️ Stack

### Frontend
- **Vite** — ultra-fast build tool
- **React 18** — UI framework
- **TypeScript** — type safety
- **TanStack React Query** — server data management (caching, retries, loading states)
- **Tailwind CSS** — utility-first styling
- **Recharts** — interactive charts
- **shadcn/ui** — accessible component library

### Backend
- **FastAPI** — modern Python API framework (automatic OpenAPI docs)
- **joblib** — model serialization (loads `model.pkl` at startup)
- **RandomForestClassifier** — pre-trained model (from scikit-learn)
- **Pydantic** — request/response validation

### Deployment
- **Docker** — containerization
- **docker-compose** — orchestration (frontend + backend + nginx)

### Data Pipeline
- **Jupyter Notebook** (`CodeBase/etl/Data_ia_foot.ipynb`) — ETL + training
- **Python scikit-learn** — model training and evaluation

---

## 🚀 Getting Started

### Prerequisites
- **Python** 3.10+
- **Node.js** 18+ (npm)
- **model.pkl** in `CodeBase/backend/` (generated from ETL notebook)

### Backend (Terminal 1)

```bash
cd CodeBase/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Ensure model.pkl is present
# (Generate from ETL notebook: joblib.dump(bundle, "model.pkl"))

# Start server
python main.py
# API running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend (Terminal 2)

```bash
cd CodeBase/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# App running at http://localhost:5173
```

### Health Check

```bash
# Backend health
curl http://localhost:8000/api/health
# Expected: {"status":"ok","model_loaded":true}

# Make a prediction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team":"France","away_team":"Mexico"}'
```

---

## 📚 Documentation

Detailed documentation is in the `docs/` folder:

| File | Content |
|------|---------|
| [docs/architecture.md](docs/architecture.md) | System design, component interactions, technology choices |
| [docs/dataset.md](docs/dataset.md) | Data description, distributions, quality, biases |
| [docs/question-predictive.md](docs/question-predictive.md) | ML problem definition, features, metrics, justification |
| [docs/user-journey.md](docs/user-journey.md) | User experience flow, UI/UX insights, satisfaction metrics |
| [docs/diagramme-sequence.md](docs/diagramme-sequence.md) | Technical sequence: frontend → backend → model → response |

---

## 📦 Project Structure

```
CodeBase/
├── backend/
│   ├── main.py              # FastAPI app (endpoints: /api/health, /api/predict, /api/stats)
│   ├── requirements.txt      # Python dependencies
│   ├── model.pkl            # Pre-trained RandomForest (joblib)
│   └── Dockerfile           # Container build
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main dashboard component
│   │   ├── PredictionForm.tsx # Form to enter teams
│   │   ├── StatsChart.tsx    # Statistics visualization
│   │   ├── api.ts           # Centralized API calls (React Query)
│   │   └── index.css        # Global styles
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── etl/
│   ├── Data_ia_foot.ipynb   # Training notebook (ETL + RandomForest)
│   └── generate_model.py    # Helper to export model.pkl
└── docker-compose.yml       # Multi-container orchestration
```

---

## 🎯 Key Features

✅ **Real-time Predictions** — Enter 2 teams, get instant result + probabilities  
✅ **Historical Statistics** — View team performance metrics and trends  
✅ **Model Transparency** — Accuracy metrics, feature importance, why this prediction  
✅ **Responsive Design** — Works on desktop and tablet  
✅ **Type-Safe** — Full TypeScript frontend + Pydantic validation backend  

---

## 🐳 Docker Deployment

```bash
cd CodeBase

# Build and run
docker-compose up --build

# Access
# Frontend: http://localhost:80 (nginx)
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## 📊 Model Details

| Metric | Value |
|--------|-------|
| Algorithm | RandomForestClassifier (100 trees, max_depth=10) |
| Train/Test Split | 80% / 20% (998 / 250 samples) |
| Features | 9 (home_avg_goals, away_avg_goals, goal_diff, home_total_matches, away_total_matches, home_wins, away_wins, year, count_teams) |
| Classes | 3 (home win, draw, away win) |
| **Accuracy** | **64.80%** |
| F1-Score (macro) | 0.63 |
| Baseline | 36% (always predict home win) |

---

## 🛠️ Development Commands

### Frontend
```bash
cd CodeBase/frontend

npm run dev         # Start dev server
npm run build       # Production build (dist/)
npm run typecheck   # TypeScript type checking
npm run preview     # Preview production build
```

### Backend
```bash
cd CodeBase/backend

python main.py                      # Start server
python -m pytest tests/ -v          # Run tests (if any)
```

### Type Checking
```bash
cd CodeBase/frontend
npm run typecheck    # Zero TypeScript errors required
```

---

## ⚡ Conventions

See [CodeBase/CLAUDE.md](CodeBase/CLAUDE.md) for detailed guidelines.

**Key principles**:
- **Server data** → use React Query (`useQuery`, `useMutation`)
- **Local state** → use `useState`
- **No global state library** (Redux, Zustand) — unnecessary
- **Styling** → Tailwind CSS + `cn()` helper
- **Components** → surgical edits only, don't rewrite working files
- **API contracts** — never change without flagging in commit

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **CORS error** | Check ports: frontend on 5173, backend on 8000. `CORSMiddleware` in `main.py` allows both. |
| **Blank chart** | Ensure `/api/stats` returns data + `<ResponsiveContainer>` wraps Recharts |
| **Model crash** | Verify `model.pkl` exists and bundle keys match backend code |
| **Team not found** | Ensure team name matches database (case-sensitive) |
| **slow response** | Profile model.predict_proba() latency or check network |

---

## 📝 Development Workflow

1. **Read** the plan file for your task (`Ressources/3.plan/`)
2. **Code** with appropriate skill (FastAPI or React)
3. **Launch** backend + frontend
4. **Test** via Playwright MCP (or manual)
5. **Document** in `CodeBase/CHANGELOG.md`
6. **Commit** with descriptive message

See [CLAUDE.md](CLAUDE.md) for full workflow details.

---

## 📄 License & Attribution

Course project (B3 — Data Science École Sup'). Dataset sourced from publicly available FIFA World Cup records.

---

## 🚀 Next Steps

- [ ] Complete backend endpoints (features validation, edge cases)
- [ ] Add team autocomplete in frontend form
- [ ] Deploy to production (Azure App Service or similar)
- [ ] Add historical prediction tracking
- [ ] Explore model explainability (SHAP values)

---

**Questions?** See [docs/](docs/) for comprehensive documentation or check [CLAUDE.md](CLAUDE.md) for development guidance.
