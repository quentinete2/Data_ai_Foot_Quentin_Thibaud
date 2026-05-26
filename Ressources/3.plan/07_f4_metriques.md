# F4 — Section métriques du modèle (`App.tsx`)

## Objectif

Afficher l'**accuracy** du modèle retournée par `/api/stats` dans la section "Performance du modèle" de `App.tsx`.

## Fichier cible

`CodeBase/frontend/src/App.tsx`

## Contexte

`stats.metrics` est déjà disponible depuis le même `useQuery` utilisé pour `StatsChart` (F3). Pas de nouvelle requête nécessaire.

Le modèle est un `RandomForestClassifier` de **classification** (pas de régression) — les métriques pertinentes sont `accuracy`, non MAE/RMSE/R².

## Code à écrire (section "Performance du modèle")

```tsx
<section className="mt-6">
  <h2 className="text-lg font-semibold">Performance du modèle</h2>
  {stats?.metrics ? (
    <div className="mt-3 grid grid-cols-1 gap-4 max-w-xs">
      <MetricCard
        label="Accuracy (test set)"
        value={`${(stats.metrics.accuracy * 100).toFixed(1)} %`}
      />
    </div>
  ) : (
    <p className="text-gray-400 text-sm">En attente des stats…</p>
  )}
</section>
```

## Composant `MetricCard` (dans le même fichier ou inline)

```tsx
function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border p-4 text-center">
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  )
}
```

## Interprétation de la métrique

| Métrique | Valeur | Signification |
|----------|--------|---------------|
| Accuracy | 64.80 % | 65 % des matchs prédits correctement sur le test set (250 matchs) |

> Le modèle est meilleur sur les victoires à domicile (F1 = 0.76) que sur les nuls (F1 = 0.25). C'est typique en prédiction de foot — les nuls sont structurellement difficiles à prédire.

## Validation

- Ouvrir `http://localhost:5173`
- La section affiche une carte avec "64.8 %" (ou la valeur exacte retournée par l'API)
- `npm run typecheck` → 0 erreur
- La métrique `accuracy` dans le type `StatsResponse` est un `number` (pas une string)

## Dépendances

- F3 doit être terminé (`stats` est déjà chargé via le même `useQuery`)
- B3 doit retourner `metrics` avec la clé `accuracy` (pas `mae`/`rmse`/`r2`)
