# Spécification — Backend FastAPI

## Responsabilités

- Charger `model.pkl` au démarrage (une seule fois)
- Exposer les endpoints REST consommés par le frontend
- Servir les fichiers statiques du frontend en production

## Endpoints

### `GET /api/health`
Vérification que l'API est opérationnelle.

**Réponse** :
```json
{ "status": "ok" }
```

---

### `POST /api/predict`
Prédit le stade attendu pour une équipe en 2026.

**Corps de la requête** (Pydantic `Features`) :
```json
{
  "nb_participations": 22,
  "taux_victoire_historique": 0.65,
  "buts_marques_moy": 1.8,
  "buts_encaisses_moy": 0.9,
  "diff_buts_moy": 0.9,
  "meilleur_stade_atteint": 6,
  "stade_dernier_tournoi": 4,
  "est_hote": 0
}
```

**Réponse** :
```json
{
  "predicted_stage": 5.2,
  "stage_label": "Finale"
}
```

**Erreur modèle non chargé** : HTTP 503

---

### `GET /api/stats`
Statistiques agrégées pour alimenter les graphiques du dashboard.

**Réponse** (à définir selon les graphiques souhaités) :
```json
{
  "top_teams": [...],
  "stage_distribution": {...},
  "metrics": { "mae": 0.8, "rmse": 1.1 }
}
```

## Structure du fichier `main.py`

```
FastAPI app
├── CORS middleware (origins: localhost:5173)
├── Chargement model.pkl au startup
├── GET  /api/health
├── POST /api/predict
├── GET  /api/stats
└── [StaticFiles — décommenté en production]
```

## Bonnes pratiques

- Une seule instance du modèle en mémoire (variable globale au module)
- Validation automatique des entrées via Pydantic — pas de validation manuelle
- Jamais de ré-entraînement en production
- Les types Pydantic doivent correspondre exactement aux types numpy attendus par sklearn

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
        UC2(["Obtenir une prediction\nPOST /api/predict"])
        UC3(["Obtenir les statistiques\nGET /api/stats"])
        UC4(["Valider les features\nvia Pydantic"])
        UC5(["Servir le front builte\nStaticFiles — prod"])
    end

    FE --> UC1
    FE --> UC2
    FE --> UC3
    ADM --> UC5
    UC2 -.->|«include»| UC4

    style FE fill:#fff,stroke:#000
    style ADM fill:#fff,stroke:#000
```

## Diagramme de classes UML — Modèles Pydantic

```mermaid
classDiagram
    class Features {
        +int nb_participations
        +float taux_victoire_historique
        +float buts_marques_moy
        +float buts_encaisses_moy
        +float diff_buts_moy
        +int meilleur_stade_atteint
        +int stade_dernier_tournoi
        +int est_hote
    }

    class PredictResponse {
        +float predicted_stage
        +str stage_label
    }

    class StatsResponse {
        +list~StatItem~ top_teams
        +dict stage_distribution
        +ModelMetrics metrics
    }

    class StatItem {
        +str label
        +float value
    }

    class ModelMetrics {
        +float mae
        +float rmse
        +float r2
    }

    Features --> PredictResponse : POST /api/predict
    StatsResponse "1" *-- "0..*" StatItem : top_teams
    StatsResponse "1" *-- "1" ModelMetrics : metrics
```

## Séquence d'une prédiction

```mermaid
sequenceDiagram
    participant FE as Frontend React
    participant API as FastAPI :8000
    participant ML as model.pkl

    FE->>API: POST /api/predict\n{8 features JSON}
    API->>API: Pydantic valide Features
    alt modèle absent
        API-->>FE: 503 model.pkl manquant
    else modèle chargé
        API->>ML: predict([[f1, f2, ..., f8]])
        ML-->>API: [4.8]
        API->>API: round → 5, label → "Finale"
        API-->>FE: {predicted_stage: 4.8, stage_label: "Finale"}
    end
```
