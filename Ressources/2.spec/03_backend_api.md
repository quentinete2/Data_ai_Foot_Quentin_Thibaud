# Spécification — Backend FastAPI

## Responsabilités

- Charger le bundle `model.pkl` au démarrage (une seule fois) : modèle RFC + dicts de stats + médians
- Exposer les endpoints REST consommés par le frontend
- Servir les fichiers statiques du frontend en production

## Endpoints

### `GET /api/health`
Vérification que l'API est opérationnelle.

**Réponse** :
```json
{ "status": "ok", "model_loaded": true }
```

---

### `POST /api/predict`
Prédit le résultat d'un match entre deux équipes.

**Corps de la requête** (Pydantic `MatchInput`) :
```json
{
  "home_team": "France",
  "away_team": "Mexico"
}
```

**Réponse** :
```json
{
  "prediction": "Victoire France",
  "confidence": 0.4829,
  "probabilities": {
    "home_win": 0.4829,
    "draw": 0.3160,
    "away_win": 0.2012
  },
  "home_stats": {
    "avg_goals": 2.1,
    "total_matches": 45,
    "wins": 28
  },
  "away_stats": {
    "avg_goals": 1.4,
    "total_matches": 19,
    "wins": 11
  }
}
```

**Erreur modèle non chargé** : HTTP 503

---

### `GET /api/stats`
Statistiques agrégées pour alimenter les graphiques du dashboard.

**Réponse** :
```json
{
  "top_teams_wins": [
    {"label": "Hungary", "value": 83.33},
    {"label": "Brazil", "value": 74.53},
    ...
  ],
  "top_teams_goals": [
    {"label": "Hungary", "value": 4.06},
    {"label": "Norway", "value": 2.73},
    ...
  ],
  "metrics": {
    "accuracy": 0.6480
  }
}
```

`top_teams_wins` : top 10 par pourcentage de victoires (min 5 matchs), valeur = pourcentage (float).
`top_teams_goals` : top 10 par moyenne de buts marqués (min 5 matchs), valeur = moyenne (float).

## Structure du fichier `main.py`

```
FastAPI app
├── CORS middleware (origins: localhost:5173)
├── Chargement model.pkl au startup (bundle dict)
├── GET  /api/health
├── POST /api/predict  ← body: {home_team, away_team}
├── GET  /api/stats    ← retourne top_teams_wins, top_teams_goals, metrics
└── [StaticFiles — décommenté en production]
```

## Bonnes pratiques

- Une seule instance du bundle en mémoire (variable globale au module)
- Validation automatique des entrées via Pydantic — pas de validation manuelle
- Jamais de ré-entraînement en production
- Pour une équipe inconnue dans les stats, renvoyer des stats à 0 plutôt qu'une erreur

## Lancer le backend

```bash
# Depuis CodeBase/backend/
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python main.py                  # http://localhost:8000
```

---

## Diagramme de cas d'utilisation — API (UML)

```mermaid
graph LR
    FE((Frontend\nReact))
    ADM((Developpeur\nOps))

    subgraph API ["Backend FastAPI :8000"]
        UC1(["Verifier la sante\nGET /api/health"])
        UC2(["Predire resultat match\nPOST /api/predict"])
        UC3(["Obtenir les statistiques\nGET /api/stats"])
        UC4(["Valider les noms equipes\nvia Pydantic MatchInput"])
        UC5(["Lookup stats home/away\ndans home_stats/away_stats"])
        UC6(["Servir le front builte\nStaticFiles — prod"])
    end

    FE --> UC1
    FE --> UC2
    FE --> UC3
    ADM --> UC6
    UC2 -.->|«include»| UC4
    UC2 -.->|«include»| UC5

    style FE fill:#fff,stroke:#000
    style ADM fill:#fff,stroke:#000
```

## Diagramme de classes UML — Modèles Pydantic

```mermaid
classDiagram
    class MatchInput {
        +str home_team
        +str away_team
    }

    class PredictResponse {
        +str prediction
        +float confidence
        +ProbDict probabilities
        +TeamStatDict home_stats
        +TeamStatDict away_stats
    }

    class ProbDict {
        +float home_win
        +float draw
        +float away_win
    }

    class TeamStatDict {
        +float avg_goals
        +int total_matches
        +int wins
    }

    class StatsResponse {
        +list~StatItem~ top_teams_wins
        +list~StatItem~ top_teams_goals
        +ModelMetrics metrics
    }

    class StatItem {
        +str label
        +float value
    }

    class ModelMetrics {
        +float accuracy
    }

    MatchInput --> PredictResponse : POST /api/predict
    PredictResponse "1" *-- "1" ProbDict : probabilities
    PredictResponse "1" *-- "2" TeamStatDict : home/away_stats
    StatsResponse "1" *-- "0..*" StatItem : top_teams_*
    StatsResponse "1" *-- "1" ModelMetrics : metrics
```

## Séquence d'une prédiction

```mermaid
sequenceDiagram
    participant FE as Frontend React
    participant API as FastAPI :8000
    participant BU as bundle (model.pkl)

    FE->>API: POST /api/predict\n{home_team, away_team}
    API->>API: Pydantic valide MatchInput
    alt bundle absent
        API-->>FE: 503 model.pkl manquant
    else bundle chargé
        API->>BU: lookup home_stats[home_team]
        API->>BU: lookup away_stats[away_team]
        API->>BU: model.predict([[9 features]])
        BU-->>API: classe predite (0/1/2)
        API->>BU: model.predict_proba([[9 features]])
        BU-->>API: [p_home, p_draw, p_away]
        API->>API: construire label prediction
        API-->>FE: {prediction, confidence, probabilities, home_stats, away_stats}
    end
```
