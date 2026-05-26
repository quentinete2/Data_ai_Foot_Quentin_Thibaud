import { useQuery } from '@tanstack/react-query'
import { BarChart3 } from 'lucide-react'
import PredictionForm from './PredictionForm'
import { getStats } from './api'

export default function App() {
  // TODO (Claude Code) : passer enabled a true une fois /api/stats pret
  const { data: stats } = useQuery({ queryKey: ['stats'], queryFn: getStats, enabled: false })

  return (
    <main className="mx-auto max-w-4xl p-6 font-sans">
      <h1 className="flex items-center gap-2 text-2xl font-bold">
        <BarChart3 className="h-6 w-6" /> Dashboard — [votre dataset]
      </h1>

      <section className="mt-6">
        <h2 className="text-lg font-semibold">Explorer les données</h2>
        {/* TODO (Claude Code) : composant StatsChart (Recharts) affichant `stats`,
            toujours dans un <ResponsiveContainer> sinon rien ne s'affiche */}
        <p className="text-gray-500">{stats ? 'Stats chargées' : 'TODO : activer /api/stats'}</p>
      </section>

      <section className="mt-6">
        <h2 className="text-lg font-semibold">Prédire</h2>
        <PredictionForm />
      </section>

      <section className="mt-6">
        <h2 className="text-lg font-semibold">Performance du modèle</h2>
        {/* TODO : métriques J2 (R²/RMSE ou accuracy/F1) */}
      </section>
    </main>
  )
}
