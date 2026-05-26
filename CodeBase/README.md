# Template projet B3 — Dashboard React + API FastAPI

Squelette à compléter **avec Claude Code**. Stack alignée sur la stack Pando (version cours).

- **frontend/** : React 18 + Vite + **TypeScript** · **TanStack React Query** (data) · **Tailwind CSS** (+ `cn()` shadcn-ready) · **lucide-react** (icônes) · **Recharts** (graphes).
- **backend/** : FastAPI (Python) + joblib (charge `model.pkl`).
- *En prod chez Pando c'est Next.js ; ici une SPA servie par 1 FastAPI → Vite.*

## Démarrer

### Backend (terminal 1)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# placez votre model.pkl ici (exporté du notebook J2 : joblib.dump(pipeline, "model.pkl"))
python main.py            # API sur http://localhost:8000  (test : /api/health)
```

### Frontend (terminal 2)
```bash
cd frontend
npm install
npm run dev               # app sur http://localhost:5173
```

## Ce qu'il reste à faire (cherchez les `TODO`)
- **backend** : définir le modèle Pydantic `Features`, compléter `/api/predict` et `/api/stats`.
- **frontend** : générer les champs du formulaire (`PredictionForm.tsx`), activer la requête stats (`App.tsx`), ajouter les graphes Recharts.

## Prompts Claude Code pour démarrer
- « Lis `backend/main.py` et `frontend/src/`, explique-moi la structure et la stack. »
- « Dans `backend/main.py`, définis le Pydantic `Features` avec `<mes features>` et complète `/api/predict`. »
- « Dans `frontend/src/PredictionForm.tsx`, génère un champ contrôlé par feature, soumets via la mutation React Query, affiche la prédiction. »
- (graphes : voir le **brief d'autonomie 15h-16h**)

## Conventions (voir CLAUDE.md)
- Données serveur → **React Query** ; state local → `useState` ; styles → **Tailwind**.
- UI : `npx shadcn@latest add <composant>` au besoin, ne pas réinventer les primitives.

## Déploiement (J4)
`npm run build` dans `frontend/` → décommentez le bloc `StaticFiles` dans `backend/main.py` → **une seule App Service**.

## En cas de blocage
- *CORS error* → `CORSMiddleware` (présent) autorise `localhost:5173`. Vérifiez les ports.
- *Graphe vide* → manque `<ResponsiveContainer>` ou `/api/stats` renvoie vide (onglet Réseau).
- *Modèle plante* → ordre/types des features ≠ entraînement J2.
- Ça casse → `git restore .` (commitez souvent !).
