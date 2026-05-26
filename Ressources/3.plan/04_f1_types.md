# F1 — Aligner les types TypeScript (`api.ts`)

## Objectif

Mettre à jour `api.ts` pour que les types TypeScript correspondent exactement aux nouvelles réponses du backend (après B2 et B3).

## Fichier cible

`CodeBase/frontend/src/api.ts`

## Types à ajouter / modifier

### Type `Features` (corps de la requête predict)

```typescript
export type Features = {
  nb_participations: number
  taux_victoire_historique: number
  buts_marques_moy: number
  buts_encaisses_moy: number
  diff_buts_moy: number
  meilleur_stade_atteint: number
  stade_dernier_tournoi: number
  est_hote: number  // 0 | 1
}
```

### Type `PredictResponse` (réponse de /api/predict)

```typescript
export type PredictResponse = {
  predicted_stage: number
  stage_label: string
}
```

### Type `StatsResponse` (réponse de /api/stats)

```typescript
export type StatsResponse = {
  top_teams: StatItem[]
  stage_distribution: Record<string, number>
  metrics: { mae: number; rmse: number; r2: number }
}
```

### Mise à jour des signatures de fonctions

```typescript
export async function predire(features: Features): Promise<PredictResponse> { ... }
export async function getStats(): Promise<StatsResponse> { ... }
```

## Pourquoi

Le `PredictionForm.tsx` utilise actuellement `Record<string, unknown>` pour `valeurs` — après F1, ce type sera `Features`, ce qui permet à TypeScript de valider les champs du formulaire.

## Validation

```bash
cd CodeBase/frontend && npm run typecheck
# → 0 erreur après avoir mis à jour PredictionForm.tsx en parallèle (F2)
```

## Dépendances

- B2 et B3 doivent être terminés pour connaître les shapes exactes des réponses
- F2 (formulaire) et F4 (métriques) dépendent des types définis ici
