# User Journey : Comment prédire un match

## Scénario utilisateur

**Persona** : Un fan de football qui veut savoir qui va gagner un futur match de Coupe du Monde.

**Goal** : Obtenir une prédiction fiable + raison (statistiques des équipes).

---

## Étapes du parcours

```mermaid
journey
    title Prédiction d'un match — User Journey
    section 1. Accès
        Accéder au dashboard: 5: User
        Voir formulaire: 5: User
    section 2. Input
        Saisir équipe domicile: 4: User
        Saisir équipe visiteur: 4: User
        Cliquer "Prédire": 5: User
    section 3. Attente
        Attendre réponse API: 3: User
        Voir spinner/loading: 3: User
    section 4. Résultat
        Lire résultat (home/draw/away): 5: User
        Voir probabilités (%): 4: User
        Consulter stats équipes: 4: User
    section 5. Exploration
        Voir graphiques historiques: 4: User
        Comparer autre match: 3: User
```

---

## Description détaillée

### 1️⃣ **Accès au dashboard**
   - **Utilisateur** accède à `http://localhost:5173` (ou prod URL)
   - **Voir** : titre "FIFA 2026 Prediction", formulaire de prédiction visible
   - **Sentiment** : 🟢 Clair, accueil chaleureux

### 2️⃣ **Saisie des équipes**
   - **Entrer** nom équipe domicile (ex: "France")
   - **Entrer** nom équipe visiteur (ex: "Mexico")
   - **Contrôle** : validation côté client (équipes dans la base)
   - **Sentiment** : 🟢 Simple, rapide, feedback immédiat

### 3️⃣ **Soumission**
   - **Cliquer** bouton "Prédire"
   - **Backend reçoit** `{home_team: "France", away_team: "Mexico"}`
   - **Attente** : ~200ms (lookup stats + inférence)
   - **Sentiment** : 🟡 Courte latence acceptable (loading spinner affiché)

### 4️⃣ **Affichage du résultat**
   - **Voir** badge avec résultat : "🏠 France favori" (home win)
   - **Voir** barres probabilité : France 62%, Nul 18%, Mexico 20%
   - **Voir** stats contexte : France avg 1.85 buts, Mexico avg 1.42
   - **Sentiment** : 🟢 Clair, confiance dans le résultat

### 5️⃣ **Exploration optionnelle**
   - **Graphiques** : top équipes (wins, buts) — Recharts intégré
   - **Metrique globale** : accuracy du modèle (64.8%) — pour transparence
   - **Nouvel essai** : formulaire reste disponible → loop
   - **Sentiment** : 🟢 Engagé, exploratif

---

## Parcours utilisateur (schéma technique)

```mermaid
sequenceDiagram
    participant User as 👤 Utilisateur
    participant Frontend as 🖥️ Frontend<br/>(React)
    participant API as 🔌 API<br/>(FastAPI)
    participant Model as 🤖 Modèle<br/>(RandomForest)
    
    User->>Frontend: 1. Visite dashboard
    Frontend->>Frontend: Rendre formulaire
    Frontend-->>User: ✅ Afficher page
    
    User->>Frontend: 2. Saisir France vs Mexico
    Frontend->>Frontend: Valider équipes
    Frontend-->>User: ✅ Feedback temps réel
    
    User->>Frontend: 3. Cliquer "Prédire"
    Frontend->>Frontend: Montrer loading spinner
    Frontend->>API: POST /api/predict<br/>{home_team, away_team}
    
    API->>API: 4. Lookup stats<br/>historiques
    API->>Model: 5. Appeler inférence<br/>(9 features)
    Model-->>API: Retourner<br/>prédiction + probas
    
    API-->>Frontend: 200 OK<br/>{prediction, probs,<br/>home_stats, away_stats}
    Frontend->>Frontend: 6. Parser réponse
    Frontend->>Frontend: Afficher badge + barres
    Frontend-->>User: ✅ Voir résultat<br/>(France 62%)
    
    User->>Frontend: 7. Consulter stats/graphes
    Frontend->>API: GET /api/stats
    API-->>Frontend: {top_teams, metrics}
    Frontend-->>User: ✅ Voir dashboards
```

---

## Emojis de satisfaction par étape

| Étape | Description | Satisfaction | Raison |
|-------|-------------|--------------|--------|
| 1️⃣ Accès | Dashboard charge | ⭐⭐⭐⭐⭐ (5/5) | Immédiat, intuitif |
| 2️⃣ Input | Saisie équipes | ⭐⭐⭐⭐ (4/5) | Rapide, pas de friction |
| 3️⃣ Attente | Réponse API | ⭐⭐⭐ (3/5) | ~200ms, acceptable mais notoire |
| 4️⃣ Résultat | Voir prédiction | ⭐⭐⭐⭐⭐ (5/5) | Clair, avec confiance |
| 5️⃣ Exploration | Graphiques/stats | ⭐⭐⭐⭐ (4/5) | Enrichissant, mais secondaire |

---

## Points clés d'UX

✅ **Réussis** :
- Formulaire simple (2 inputs)
- Résultat visuel (badge + barres)
- Stats contextuelles (pourquoi ce résultat)

⚠️ **À améliorer** :
- Historique des prédictions (sauvegarde session)
- Affichage de confiance (accuracy locale)
- Suggestions d'équipes (autocomplete)

