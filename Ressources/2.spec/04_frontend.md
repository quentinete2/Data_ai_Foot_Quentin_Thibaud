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
- Graphique : top 10 équipes par pourcentage de victoires (`top_teams_wins`)
- Source : `GET /api/stats`
- Composant Recharts dans `<ResponsiveContainer width="100%" height={300}>`
- Axe X : nom équipe, Axe Y : pourcentage de victoires

### 2. Formulaire de prédiction
- **2 champs texte** : `home_team` et `away_team` (noms d'équipes)
- Mutation React Query → `POST /api/predict`
- Affiche le résultat : prédiction (ex. "Victoire France"), confiance + probabilités home/draw/away

### 3. Performance du modèle
- Affiche l'**accuracy** du modèle (64.80 %) sur le test set
- Source : `GET /api/stats` → `metrics.accuracy`

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
| TypeScript error sur la réponse | Type `MatchInput` ou `PredictResponse` désynchronisé | Aligner `src/api.ts` avec le modèle Pydantic du backend |
| "Équipe inconnue" | Nom d'équipe pas dans les 84 équipes connues | Afficher un message "stats non disponibles" sans planter |

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
        UC1(["Voir le graphique\ntop equipes victoires"])
        UC2(["Saisir les noms des equipes\nhome vs away"])
        UC3(["Soumettre la prediction"])
        UC4(["Lire le resultat\nprediction + probabilites"])
        UC5(["Consulter la metrique\nAccuracy du modele"])
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
        +MatchInput valeurs
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

    class MatchInput {
        +string home_team
        +string away_team
    }

    class PredictResponse {
        +string prediction
        +number confidence
        +object probabilities
        +object home_stats
        +object away_stats
    }

    class StatItem {
        +string label
        +number value
    }

    App "1" *-- "1" PredictionForm : contient
    App "1" *-- "1" StatsChart : contient
    App "1" *-- "1" MetricCard : contient
    PredictionForm --> MatchInput : utilise
    PredictionForm --> PredictResponse : affiche
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
    API-->>RQ: top_teams_wins + top_teams_goals + metrics
    RQ-->>C: data
    C-->>U: Graphique + carte accuracy

    Note over C,RQ: Soumission du formulaire
    U->>C: Saisit "France" vs "Mexico" + clic Predire
    C->>RQ: useMutation predire({home_team, away_team})
    RQ->>API: POST /api/predict
    API-->>RQ: {prediction, confidence, probabilities, ...}
    RQ-->>C: mutation.data
    C-->>U: "Victoire France" — confiance 48.29%
```
