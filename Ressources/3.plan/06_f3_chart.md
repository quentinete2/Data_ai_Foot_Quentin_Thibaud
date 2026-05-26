# F3 — Composant `StatsChart` (Recharts)

## Objectif

Créer `StatsChart.tsx` qui affiche un `BarChart` Recharts à partir de `top_teams` (les 10 équipes avec le plus de victoires), et l'intégrer dans `App.tsx` avec la query activée.

## Fichiers cibles

- Nouveau : `CodeBase/frontend/src/StatsChart.tsx`
- Modifier : `CodeBase/frontend/src/App.tsx`

## Composant `StatsChart.tsx`

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import type { StatItem } from './api'

type Props = { data: StatItem[] }

export default function StatsChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 4, right: 16, bottom: 40, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" angle={-35} textAnchor="end" tick={{ fontSize: 11 }} />
        <YAxis />
        <Tooltip />
        <Bar dataKey="value" fill="#1d4ed8" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
```

## Modifications dans `App.tsx`

1. Importer `StatsChart`
2. Passer `enabled: true` sur le `useQuery`
3. Gérer les états `isLoading` / `isError`
4. Afficher `<StatsChart>` avec `stats.top_teams`

```tsx
import StatsChart from './StatsChart'

// Dans le composant :
const { data: stats, isLoading, isError } = useQuery({
  queryKey: ['stats'],
  queryFn: getStats,
  enabled: true,  // ← changer ici
})

// Dans le JSX de la section "Explorer les données" :
{isLoading && <p className="text-gray-400 text-sm">Chargement…</p>}
{isError  && <p className="text-red-500 text-sm">Impossible de charger les stats.</p>}
{stats    && <StatsChart data={stats.top_teams} />}
```

## Points importants

- `<ResponsiveContainer>` est **obligatoire** — sans lui le graphique ne s'affiche pas (height = 0)
- Le `margin.bottom` à 40 laisse de la place pour les labels d'équipe inclinés
- `dataKey="label"` et `dataKey="value"` correspondent au type `StatItem` de `api.ts`

## Validation

- Lancer backend + frontend, ouvrir `http://localhost:5173`
- La section "Explorer les données" doit afficher un graphique à barres avec 10 équipes
- Pas de console errors

## Dépendances

- B3 doit être terminé (`/api/stats` doit retourner `top_teams`)
- F1 doit être terminé (type `StatsResponse` dans `api.ts`)
