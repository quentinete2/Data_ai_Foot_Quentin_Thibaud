# Tableau de Bord de Prédiction FIFA Coupe du Monde 2026

> **Prédisez les résultats des matchs** à partir de données historiques de la Coupe du Monde et du machine learning. Une application fullstack combinant un frontend React, un backend FastAPI et un modèle RandomForest pré-entraîné.

---

## Présentation du projet

**Quoi** : Un tableau de bord web qui prédit l'issue des matchs de la Coupe du Monde FIFA (victoire à domicile / match nul / victoire à l'extérieur) à partir de 92 ans de données historiques (1930–2022, 1248 matchs).

**Pour qui** : Les passionnés de football, les analystes et les enseignants souhaitant explorer les prédictions sportives par le machine learning.

**Jeu de données** : Données historiques de la Coupe du Monde FIFA
  - **Source** : GitHub (disponible publiquement)
  - **Taille** : 1248 matchs × 10 caractéristiques
  - **Période** : 1930–2022 (24 tournois)
  - **Classes** : 3 (victoire à domicile : 36 %, match nul : 24 %, victoire à l'extérieur : 40 %)

**Tâche ML** : Classification multiclasse (RandomForestClassifier, 100 arbres)  
**Précision** : 64,80 % sur le jeu de test (référence : 36 % → **+78 % de gain**)

---

## Stack technique

### Frontend
- **Vite** — outil de build ultra-rapide
- **React 18** — framework UI
- **TypeScript** — typage statique
- **TanStack React Query** — gestion des données serveur (cache, retry, états de chargement)
- **Tailwind CSS** — styles utilitaires
- **Recharts** — graphiques interactifs
- **shadcn/ui** — bibliothèque de composants accessibles

### Backend
- **FastAPI** — framework Python moderne (documentation OpenAPI automatique)
- **joblib** — sérialisation du modèle (charge `model.pkl` au démarrage)
- **RandomForestClassifier** — modèle pré-entraîné (scikit-learn)
- **Pydantic** — validation des requêtes et réponses

### Déploiement
- **Docker** — conteneurisation
- **docker-compose** — orchestration (frontend + backend + nginx)

### Pipeline de données
- **Jupyter Notebook** (`CodeBase/etl/Data_ia_foot.ipynb`) — ETL + entraînement
- **Python scikit-learn** — entraînement et évaluation du modèle

---

## Démarrage rapide

### Prérequis
- **Python** 3.10+
- **Node.js** 18+ (npm)
- **model.pkl** dans `CodeBase/backend/` (généré depuis le notebook ETL)

### Backend (Terminal 1)

```bash
cd CodeBase/backend

# Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Vérifier que model.pkl est présent
# (Générer depuis le notebook ETL : joblib.dump(bundle, "model.pkl"))

# Démarrer le serveur
python main.py
# API disponible sur http://localhost:8000
# Documentation sur http://localhost:8000/docs
```

### Frontend (Terminal 2)

```bash
cd CodeBase/frontend

# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm run dev
# Application disponible sur http://localhost:5173
```

### Vérification

```bash
# Santé du backend
curl http://localhost:8000/api/health
# Attendu : {"status":"ok","model_loaded":true}

# Effectuer une prédiction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team":"France","away_team":"Mexico"}'
```

---

## Documentation

La documentation détaillée se trouve dans le dossier `docs/` :

| Fichier | Contenu |
|---------|---------|
| [docs/architecture.md](docs/architecture.md) | Conception du système, interactions entre composants, choix technologiques |
| [docs/dataset.md](docs/dataset.md) | Description des données, distributions, qualité, biais |
| [docs/question-predictive.md](docs/question-predictive.md) | Définition du problème ML, features, métriques, justification |
| [docs/user-journey.md](docs/user-journey.md) | Parcours utilisateur, insights UI/UX, métriques de satisfaction |
| [docs/diagramme-sequence.md](docs/diagramme-sequence.md) | Séquence technique : frontend → backend → modèle → réponse |

---

## Structure du projet

```
CodeBase/
├── backend/
│   ├── main.py              # Application FastAPI (endpoints : /api/health, /api/predict, /api/stats)
│   ├── requirements.txt      # Dépendances Python
│   ├── model.pkl            # RandomForest pré-entraîné (joblib)
│   └── Dockerfile           # Build du conteneur
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Composant principal du tableau de bord
│   │   ├── PredictionForm.tsx # Formulaire de saisie des équipes
│   │   ├── StatsChart.tsx    # Visualisation des statistiques
│   │   ├── api.ts           # Appels API centralisés (React Query)
│   │   └── index.css        # Styles globaux
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── etl/
│   ├── Data_ia_foot.ipynb   # Notebook d'entraînement (ETL + RandomForest)
│   └── generate_model.py    # Script d'export de model.pkl
└── docker-compose.yml       # Orchestration multi-conteneurs
```

---

## Fonctionnalités clés

- **Prédictions en temps réel** — Entrez 2 équipes, obtenez instantanément un résultat + les probabilités
- **Statistiques historiques** — Consultez les métriques de performance des équipes et les tendances
- **Transparence du modèle** — Métriques de précision, importance des features, explication de la prédiction
- **Design responsive** — Compatible bureau et tablette
- **Typage complet** — Frontend TypeScript + validation Pydantic côté backend

---

## Déploiement Docker

```bash
cd CodeBase

# Construire et démarrer
docker-compose up --build

# Accès
# Frontend : http://localhost:80 (nginx)
# Backend : http://localhost:8000
# Documentation : http://localhost:8000/docs
```

---

## Détails du modèle

| Métrique | Valeur |
|----------|--------|
| Algorithme | RandomForestClassifier (100 arbres, max_depth=10) |
| Découpage train/test | 80 % / 20 % (998 / 250 échantillons) |
| Features | 9 (home_avg_goals, away_avg_goals, goal_diff, home_total_matches, away_total_matches, home_wins, away_wins, year, count_teams) |
| Classes | 3 (victoire domicile, match nul, victoire extérieur) |
| **Précision** | **64,80 %** |
| F1-Score (macro) | 0,63 |
| Référence | 36 % (toujours prédire victoire à domicile) |

---

## Commandes de développement

### Frontend
```bash
cd CodeBase/frontend

npm run dev         # Démarrer le serveur de développement
npm run build       # Build de production (dist/)
npm run typecheck   # Vérification des types TypeScript
npm run preview     # Prévisualiser le build de production
```

### Backend
```bash
cd CodeBase/backend

python main.py                      # Démarrer le serveur
python -m pytest tests/ -v          # Lancer les tests (si présents)
```

### Vérification des types
```bash
cd CodeBase/frontend
npm run typecheck    # Zéro erreur TypeScript requise
```

---

## Conventions

Voir [CodeBase/CLAUDE.md](CodeBase/CLAUDE.md) pour les directives détaillées.

**Principes clés** :
- **Données serveur** → utiliser React Query (`useQuery`, `useMutation`)
- **État local** → utiliser `useState`
- **Pas de librairie d'état global** (Redux, Zustand) — inutile
- **Styles** → Tailwind CSS + helper `cn()`
- **Composants** → éditions chirurgicales uniquement, ne pas réécrire les fichiers qui fonctionnent
- **Contrats API** — ne jamais modifier sans le signaler dans le commit

---

## Dépannage

| Problème | Solution |
|----------|----------|
| **Erreur CORS** | Vérifier les ports : frontend sur 5173, backend sur 8000. `CORSMiddleware` dans `main.py` autorise les deux. |
| **Graphique vide** | Vérifier que `/api/stats` retourne des données + que `<ResponsiveContainer>` encadre Recharts |
| **Crash du modèle** | Vérifier que `model.pkl` existe et que les clés du bundle correspondent au code backend |
| **Équipe introuvable** | Vérifier que le nom de l'équipe correspond à la base de données (sensible à la casse) |
| **Réponse lente** | Profiler la latence de `model.predict_proba()` ou vérifier le réseau |

---

## Workflow de développement

1. **Lire** le fichier plan de la tâche (`Ressources/3.plan/`)
2. **Coder** avec le bon skill (FastAPI ou React)
3. **Lancer** le backend + frontend
4. **Tester** via Playwright MCP (ou manuellement)
5. **Documenter** dans `CodeBase/CHANGELOG.md`
6. **Commiter** avec un message descriptif

Voir [CLAUDE.md](CLAUDE.md) pour les détails complets du workflow.

---

## Licence et attribution

Projet de cours (B3 — Data Science École Sup'). Jeu de données issu des archives publiques de la FIFA Coupe du Monde.

---

## Prochaines étapes

- [ ] Compléter les endpoints backend (validation des features, cas limites)
- [ ] Ajouter l'autocomplétion des équipes dans le formulaire frontend
- [ ] Déployer en production (Azure App Service ou similaire)
- [ ] Ajouter le suivi historique des prédictions
- [ ] Explorer l'explicabilité du modèle (valeurs SHAP)

---

**Questions ?** Consultez [docs/](docs/) pour la documentation complète ou [CLAUDE.md](CLAUDE.md) pour les directives de développement.