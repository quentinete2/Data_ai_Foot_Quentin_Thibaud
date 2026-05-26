# F1 — Aligner les types TypeScript (`api.ts`)

## Objectif

Mettre à jour `api.ts` pour que les types TypeScript correspondent exactement aux nouvelles réponses du backend (après B2 et B3).

## Fichier cible

`CodeBase/frontend/src/api.ts`

## Types à ajouter / modifier

### Type `MatchInput` (corps de la requête predict)

```typescript
export type MatchInput = {
  home_team: string
  away_team: string
}
```

### Type `PredictResponse` (réponse de /api/predict)

```typescript
export type TeamStats = {
  avg_goals: number
  total_matches: number
  wins: number
}

export type PredictResponse = {
  prediction: string   // ex: "Victoire France" | "Match Nul" | "Victoire Mexico"
  confidence: number   // probabilité de la classe prédite
  probabilities: {
    home_win: number
    draw: number
    away_win: number
  }
  home_stats: TeamStats
  away_stats: TeamStats
}
```

### Type `StatItem` (partagé)

```typescript
export type StatItem = {
  label: string
  value: number
}
```

### Type `StatsResponse` (réponse de /api/stats)

```typescript
export type StatsResponse = {
  top_teams_wins: StatItem[]
  top_teams_goals: StatItem[]
  metrics: { accuracy: number }
}
```

### Mise à jour des signatures de fonctions

```typescript
export async function predire(match: MatchInput): Promise<PredictResponse> {
  const res = await fetch('/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(match),
  })
  if (!res.ok) throw new Error(`predict error ${res.status}`)
  return res.json()
}

export async function getStats(): Promise<StatsResponse> {
  const res = await fetch('/api/stats')
  if (!res.ok) throw new Error(`stats error ${res.status}`)
  return res.json()
}
```

## Pourquoi

Le `PredictionForm.tsx` utilisait un type vague — après F1, il recevra `MatchInput` (2 champs texte) et affichera `PredictResponse` (prediction + probabilities), ce qui permet à TypeScript de valider tous les accès.

## Validation

```bash
cd CodeBase/frontend && npm run typecheck
# → 0 erreur après avoir mis à jour PredictionForm.tsx en parallèle (F2)
```

## Dépendances

- B2 et B3 doivent être terminés pour connaître les shapes exactes des réponses
- F2 (formulaire) et F4 (métriques) dépendent des types définis ici
