# Spécification — Pipeline ETL

## Sources de données

| Fichier | Lignes | Colonnes clés |
|---------|--------|---------------|
| `matches.csv` | 1 248 | home_team_name, away_team_name, home_team_score, away_team_score, match_date, tournament_id |
| `tournaments.csv` | 30 | tournament_id, year, host_country, count_teams |

## Objectif

Transformer les matchs bruts en **features agrégées par équipe** (statistiques historiques globales), puis construire un dataset match-level pour entraîner un classificateur de résultat de match.

## Étapes du notebook (ordre)

1. Charger `matches.csv` et `tournaments.csv` depuis GitHub
2. Merger `tournaments` sur `tournament_id` pour récupérer `year`, `host_country`, `count_teams`
3. Calculer la cible `result` : 0 = victoire équipe à domicile, 1 = match nul, 2 = victoire équipe à l'extérieur
4. Créer les statistiques globales par équipe (`create_team_features`) :
   - `avg_goals` : moyenne de buts marqués par match
   - `total_matches` : nombre total de matchs joués
   - `wins` : nombre de victoires (résultat == 0 pour home, résultat == 2 pour away)
5. Construire le dataset modèle `df_model` et y ajouter les features home/away
6. Entraîner le `RandomForestClassifier`
7. Exporter le bundle : `joblib.dump(bundle, "backend/model.pkl")`

## Features du modèle (9 features par match)

| Feature | Type | Description |
|---------|------|-------------|
| `home_avg_goals` | float | Moyenne de buts marqués par match par l'équipe à domicile |
| `away_avg_goals` | float | Moyenne de buts marqués par match par l'équipe à l'extérieur |
| `goal_diff` | float | `home_avg_goals − away_avg_goals` |
| `home_total_matches` | int | Nombre total de matchs joués (équipe domicile) |
| `away_total_matches` | int | Nombre total de matchs joués (équipe extérieur) |
| `home_wins` | int | Nombre de victoires (équipe domicile) |
| `away_wins` | int | Nombre de victoires (équipe extérieur) |
| `year` | int | Année du tournoi (médiane utilisée à l'inférence) |
| `count_teams` | int | Nombre d'équipes dans le tournoi (médiane utilisée à l'inférence) |

## Target

`result` : résultat du match

| Valeur | Signification |
|--------|---------------|
| 0 | Victoire équipe à domicile |
| 1 | Match nul |
| 2 | Victoire équipe à l'extérieur |

Distribution : 0 = 677 matchs, 1 = 253, 2 = 318 (sur 1 248 totaux)

## Règle de split

Split aléatoire : `train_test_split(X, y, test_size=0.2, random_state=42)` → 998 train / 250 test.

> Pas de split temporel ici — le modèle prédit le résultat d'un match à partir des stats globales de chaque équipe (pas de look-ahead sur le tournoi).

## Export du bundle

```python
import joblib

bundle = {
    "model": model,
    "home_stats": home_stats,   # dict team_name → {avg_goals, total_matches, wins}
    "away_stats": away_stats,   # même structure pour les stats extérieur
    "median_year": median_year,
    "median_count_teams": median_count_teams,
}
joblib.dump(bundle, "backend/model.pkl")
```

Le backend charge ce bundle une seule fois au démarrage : `bundle = joblib.load("model.pkl")`.

---

## Diagramme entité-relation (UML ER)

```mermaid
erDiagram
    MATCH {
        string home_team_name
        string away_team_name
        int home_team_score
        int away_team_score
        string match_date
        string tournament_id
    }

    TOURNAMENT {
        string tournament_id
        int year
        string host_country
        int count_teams
    }

    TEAM_STATS {
        string team PK
        float avg_goals
        int total_matches
        int wins
    }

    MATCH_FEATURES {
        float home_avg_goals
        float away_avg_goals
        float goal_diff
        int home_total_matches
        int away_total_matches
        int home_wins
        int away_wins
        int year
        int count_teams
        int result
    }

    MATCH }o--|| TOURNAMENT : "appartient a"
    MATCH }o--o{ TEAM_STATS : "agregee vers"
    TEAM_STATS ||--o{ MATCH_FEATURES : "alimente"
```

## Diagramme de cas d'utilisation — ETL (UML)

```mermaid
graph LR
    DS((Data\nScientist))
    SYS((sklearn\nRFC))

    subgraph NB ["Notebook Jupyter"]
        UC1(["Charger les CSV bruts"])
        UC2(["Merger tournaments"])
        UC3(["Calculer result (0/1/2)"])
        UC4(["Creer stats par equipe"])
        UC5(["Construire df_model"])
        UC6(["Entrainer RandomForestClassifier"])
        UC7(["Evaluer accuracy / f1"])
        UC8(["Exporter bundle model.pkl"])
    end

    DS --> UC1
    DS --> UC6
    DS --> UC7
    UC1 -.->|«include»| UC2
    UC2 -.->|«include»| UC3
    UC3 -.->|«include»| UC4
    UC4 -.->|«include»| UC5
    UC5 -.->|«include»| UC6
    UC6 -.->|«include»| UC7
    UC7 -.->|«include»| UC8
    SYS --> UC6
    SYS --> UC8

    style DS fill:#fff,stroke:#000
    style SYS fill:#fff,stroke:#000
```
