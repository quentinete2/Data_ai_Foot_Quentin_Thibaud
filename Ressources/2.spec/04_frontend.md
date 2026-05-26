# Spécification — Frontend React

## Stack technique

| Outil | Rôle |
|-------|------|
| React 18 | UI library |
| Vite | Build tool (HMR rapide en dev) |
| TypeScript | Typage statique |
| React Query (`@tanstack/react-query`) | Cache et synchronisation des données serveur |
| shadcn/ui | Composants UI accessibles |
| Recharts | Graphiques (toujours dans `<ResponsiveContainer>`) |

## Sections du dashboard (`App.tsx`)

### 1. Stats historiques
- Graphique : distribution des stades atteints par les meilleures équipes
- Source : `GET /api/stats`
- Composant Recharts dans `<ResponsiveContainer width="100%" height={300}>`

### 2. Formulaire de prédiction
- Un champ par feature (8 champs)
- Validation côté client : tous les champs numériques requis
- Mutation React Query → `POST /api/predict`
- Affiche le résultat : stade prédit + label

### 3. Performance du modèle
- Affiche MAE et RMSE sur le test set 2022
- Source : `GET /api/stats`

## Règles d'architecture frontend

- **Tous les appels API dans `src/api.ts`** — jamais de `fetch` dans un composant
- **Données serveur → `useQuery` / `useMutation`** (React Query)
- **État local (UI) → `useState`**
- **Pas de state global** (Redux, Zustand, Context API pour les données)
- Import alias : `@/` pointe sur `src/`
- Ajouter des composants shadcn : `npx shadcn@latest add <composant>`

## Gestion des erreurs courantes

| Symptôme | Cause probable | Solution |
|----------|---------------|----------|
| Graphique blanc | `<ResponsiveContainer>` manquant ou `/api/stats` vide | Wrapper + vérifier la réponse API |
| Erreur CORS | Ports frontend/backend ne correspondent pas | Vérifier que le backend écoute sur 8000 et le frontend sur 5173 |
| TypeScript error sur la réponse | Type `Features` désynchronisé | Aligner `src/api.ts` avec le modèle Pydantic du backend |

## Commandes

```bash
# Depuis CodeBase/frontend/
npm install
npm run dev          # http://localhost:5173
npm run typecheck    # vérifier les types sans builder
npm run build        # production → dist/
```

---

## Diagramme de cas d'utilisation — Frontend (UML)

```mermaid
graph LR
    U((Utilisateur))

    subgraph DASH ["Dashboard React :5173"]
        UC1(["Voir le graphique\ndes meilleures equipes"])
        UC2(["Remplir les 8 features\nd'une equipe"])
        UC3(["Soumettre la prediction"])
        UC4(["Lire le resultat\nstade predit + label"])
        UC5(["Consulter les metriques\nMAE · RMSE · R2"])
    end

    U --> UC1
    U --> UC2
    U --> UC5
    UC2 -.->|«include»| UC3
    UC3 -.->|«include»| UC4

    style U fill:#fff,stroke:#000
```

## Diagramme de classes UML — Composants React

```mermaid
classDiagram
    class App {
        +StatsResponse stats
        +useQuery() void
        +render() JSX
    }

    class PredictionForm {
        +Features valeurs
        +UseMutation mutation
        +onSubmit(e FormEvent) void
        +render() JSX
    }

    class StatsChart {
        +StatItem[] data
        +render() JSX
    }

    class MetricCard {
        +string label
        +string value
        +render() JSX
    }

    class Features {
        +number nb_participations
        +number taux_victoire_historique
        +number buts_marques_moy
        +number buts_encaisses_moy
        +number diff_buts_moy
        +number meilleur_stade_atteint
        +number stade_dernier_tournoi
        +number est_hote
    }

    class StatItem {
        +string label
        +number value
    }

    App "1" *-- "1" PredictionForm : contient
    App "1" *-- "1" StatsChart : contient
    App "1" *-- "3" MetricCard : contient
    PredictionForm --> Features : utilise
    StatsChart --> StatItem : liste
```

## Séquence des interactions (UML)

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant C as Composant React
    participant RQ as React Query Cache
    participant API as FastAPI :8000

    Note over C,RQ: Au montage — StatsChart + MetricCard
    C->>RQ: useQuery(['stats'])
    RQ->>API: GET /api/stats
    API-->>RQ: top_teams + metrics
    RQ-->>C: data
    C-->>U: Graphique + cartes metriques

    Note over C,RQ: Soumission du formulaire
    U->>C: Remplit 8 champs + clic Predire
    C->>RQ: useMutation predire(features)
    RQ->>API: POST /api/predict
    API-->>RQ: predicted_stage + stage_label
    RQ-->>C: mutation.data
    C-->>U: Demi-finales (4.8)
```
