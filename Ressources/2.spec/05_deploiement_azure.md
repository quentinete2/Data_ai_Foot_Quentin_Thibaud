# Spécification — Déploiement Azure (futur)

> **Statut** : hors scope du projet actuel — à traiter après validation du fonctionnement local.

## Objectif

Déployer l'application complète (backend FastAPI + frontend buildé + modèle `model.pkl`) sur Azure.

## Approche recommandée : Azure App Service

1. **Builder le frontend** : `npm run build` → génère `dist/`
2. **Activer les StaticFiles** dans `backend/main.py` (bloc commenté) pour servir `dist/`
3. **Conteneriser** avec Docker (un seul container FastAPI + statiques)
4. **Pousser sur Azure Container Registry (ACR)**
5. **Déployer sur Azure App Service** (plan B1 minimum pour ML)

## Artefacts à préparer

- `Dockerfile` à la racine de `CodeBase/backend/`
- `model.pkl` inclus dans l'image Docker (ou stocké sur Azure Blob Storage)
- Variables d'environnement : ports, CORS origin en production

## Points d'attention

- `model.pkl` contient des objets sklearn sérialisés — ne pas changer la version de scikit-learn entre entraînement et déploiement
- Taille de l'image : les modèles sklearn sont légers, pas de problème
- Coût Azure : App Service B1 ~13 €/mois ; Free tier (F1) possible mais limité en RAM

## Ordre des étapes (quand le moment viendra)

1. Valider que `npm run build` + StaticFiles fonctionne en local
2. Écrire le `Dockerfile`
3. Tester l'image Docker en local (`docker build` + `docker run`)
4. Créer un Azure Container Registry
5. Créer un Azure App Service
6. Configurer le CI/CD (GitHub Actions) pour déploiement automatique

---

## Diagramme de cas d'utilisation — Déploiement (UML)

```mermaid
graph TB
    DEV((Developpeur))
    GH((GitHub\nActions))

    subgraph AZURE ["Services Azure"]
        UC1(["Stocker l'image Docker\nAzure Container Registry"])
        UC2(["Executer le container\nAzure App Service"])
        UC3(["Exposer l'URL publique\nhttps://app.azurewebsites.net"])
    end

    subgraph LOCAL ["Actions locales"]
        UC4(["Builder le frontend\nnpm run build"])
        UC5(["Construire l'image Docker\ndocker build"])
        UC6(["Pousser sur ACR\ndocker push"])
    end

    DEV --> UC4
    DEV --> UC5
    UC4 -.->|«include»| UC5
    UC5 -.->|«include»| UC6
    UC6 --> UC1
    UC1 --> UC2
    UC2 --> UC3
    GH -.->|«extend» CI/CD auto| UC5

    style DEV fill:#fff,stroke:#000
    style GH fill:#fff,stroke:#000
```

## Diagramme de classes UML — Infrastructure Docker

```mermaid
classDiagram
    class DockerImage {
        +string base = "python:3.11-slim"
        +string workdir = "/app"
        +model_pkl : fichier
        +dist_react : dossier
        +requirements_txt : fichier
        +build() void
        +push(registry ACR) void
    }

    class AzureContainerRegistry {
        +string name
        +string loginServer
        +pull(tag) DockerImage
        +push(image) void
    }

    class AzureAppService {
        +string plan = "B1"
        +int port = 8000
        +string url
        +deploy(image DockerImage) void
        +start() void
    }

    class FastAPIApp {
        +Pipeline model
        +DataFrame matches_df
        +predict(Features) PredictResponse
        +stats() StatsResponse
        +mount_static(dist) void
    }

    DockerImage --> FastAPIApp : contient
    AzureContainerRegistry "1" --> "1..*" DockerImage : stocke
    AzureAppService --> AzureContainerRegistry : tire l'image
    AzureAppService --> FastAPIApp : execute
```
