import { useQuery } from '@tanstack/react-query'
import { BarChart3 } from 'lucide-react'
import PredictionForm from './PredictionForm'
import StatsChart from './StatsChart'
import { getStats } from './api'

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border p-4 text-center">
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  )
}

export default function App() {
  const { data: stats, isLoading, isError } = useQuery({
    queryKey: ['stats'],
    queryFn: getStats,
    enabled: true,
  })

  return (
    <main className="mx-auto max-w-4xl p-6 font-sans">
      <h1 className="flex items-center gap-2 text-2xl font-bold">
        <BarChart3 className="h-6 w-6" /> Dashboard — FIFA WC 2026
      </h1>

      <section className="mt-6">
        <h2 className="text-lg font-semibold">Score de forme — WC 2026</h2>
        <p className="text-xs text-gray-500 mb-2">
          Score composite : taux de victoires (50 %) + buts/match (30 %) + expérience (20 %), normalisé 0–100.
        </p>
        {isLoading && <p className="text-gray-400 text-sm">Chargement…</p>}
        {isError && <p className="text-red-500 text-sm">Impossible de charger les stats.</p>}
        {stats && <StatsChart data={stats.form_scores} />}
      </section>

      <section className="mt-6">
        <h2 className="text-lg font-semibold">Prédire</h2>
        <PredictionForm />
      </section>

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
    </main>
  )
}
