# F4 — Section métriques du modèle (`App.tsx`)

## Objectif

Afficher les métriques MAE, RMSE et R² retournées par `/api/stats` dans la section "Performance du modèle" de `App.tsx`.

## Fichier cible

`CodeBase/frontend/src/App.tsx` — section ligne 28-30

## Contexte

`stats.metrics` est déjà disponible depuis le même `useQuery` utilisé pour `StatsChart` (F3). Pas de nouvelle requête nécessaire.

## Code à écrire (section "Performance du modèle")

```tsx
<section className="mt-6">
  <h2 className="text-lg font-semibold">Performance du modèle</h2>
  {stats?.metrics ? (
    <div className="mt-3 grid grid-cols-3 gap-4">
      <MetricCard label="MAE" value={stats.metrics.mae.toFixed(2)} />
      <MetricCard label="RMSE" value={stats.metrics.rmse.toFixed(2)} />
      <MetricCard label="R²" value={stats.metrics.r2.toFixed(2)} />
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

## Interprétation des métriques (à titre informatif)

| Métrique | Signification | Valeur typique pour ce modèle |
|----------|--------------|-------------------------------|
| MAE | Erreur absolue moyenne sur `stade_atteint` (1–6) | ~0.8 = erreur de ±1 stade |
| RMSE | Erreur quadratique moyenne | ~1.0 |
| R² | Part de variance expliquée | ~0.6 = bon pour ce type de données |

## Validation

- Ouvrir `http://localhost:5173`
- La section affiche 3 cartes avec les valeurs numériques
- `npm run typecheck` → 0 erreur

## Dépendances

- F3 doit être terminé (`stats` est déjà chargé via le même `useQuery`)
- B3 doit retourner `metrics` avec les bonnes clés (`mae`, `rmse`, `r2`)
