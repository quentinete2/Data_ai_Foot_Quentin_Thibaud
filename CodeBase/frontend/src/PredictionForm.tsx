import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { predire } from './api'
import type { MatchInput } from './api'

const INITIAL: MatchInput = { home_team: 'France', away_team: 'Brazil' }

type FieldErrors = { home_team?: string; away_team?: string }

export default function PredictionForm() {
  const [valeurs, setValeurs] = useState<MatchInput>(INITIAL)
  const [errors, setErrors] = useState<FieldErrors>({})

  const mutation = useMutation({ mutationFn: predire })

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed: MatchInput = {
      home_team: valeurs.home_team.trim(),
      away_team: valeurs.away_team.trim(),
    }
    const newErrors: FieldErrors = {}
    if (!trimmed.home_team) newErrors.home_team = "Le nom de l'équipe à domicile est requis"
    if (!trimmed.away_team) newErrors.away_team = "Le nom de l'équipe à l'extérieur est requis"
    setErrors(newErrors)
    if (Object.keys(newErrors).length > 0) return
    mutation.mutate(trimmed)
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium" htmlFor="home_team">
          Équipe à domicile
        </label>
        <input
          id="home_team"
          type="text"
          value={valeurs.home_team}
          onChange={(e) => {
            setValeurs((prev) => ({ ...prev, home_team: e.target.value }))
            setErrors((prev) => ({ ...prev, home_team: undefined }))
          }}
          placeholder="ex: France"
          className="rounded border px-2 py-1 text-sm"
        />
        {errors.home_team && (
          <p className="text-red-500 text-xs">{errors.home_team}</p>
        )}
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium" htmlFor="away_team">
          Équipe à l'extérieur
        </label>
        <input
          id="away_team"
          type="text"
          value={valeurs.away_team}
          onChange={(e) => {
            setValeurs((prev) => ({ ...prev, away_team: e.target.value }))
            setErrors((prev) => ({ ...prev, away_team: undefined }))
          }}
          placeholder="ex: Brazil"
          className="rounded border px-2 py-1 text-sm"
        />
        {errors.away_team && (
          <p className="text-red-500 text-xs">{errors.away_team}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={mutation.isPending}
        className="rounded bg-blue-700 px-4 py-2 text-white text-sm font-medium hover:bg-blue-800 disabled:opacity-50"
      >
        {mutation.isPending ? 'Prédiction en cours…' : 'Prédire'}
      </button>

      {mutation.isError && (
        <p className="text-red-500 text-sm">Erreur lors de la prédiction.</p>
      )}

      {mutation.data && (
        <div className="rounded-lg bg-green-50 p-4 mt-2 flex flex-col gap-3">
          <div>
            <p className="text-sm text-gray-600">Résultat prédit</p>
            <p className="text-2xl font-bold">{mutation.data.prediction}</p>
            <p className="text-sm text-gray-500">
              Confiance : {(mutation.data.confidence * 100).toFixed(1)} %
            </p>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center text-sm">
            <div className="rounded border p-2">
              <p className="font-semibold">{(mutation.data.probabilities.home_win * 100).toFixed(1)} %</p>
              <p className="text-gray-500">Dom.</p>
            </div>
            <div className="rounded border p-2">
              <p className="font-semibold">{(mutation.data.probabilities.draw * 100).toFixed(1)} %</p>
              <p className="text-gray-500">Nul</p>
            </div>
            <div className="rounded border p-2">
              <p className="font-semibold">{(mutation.data.probabilities.away_win * 100).toFixed(1)} %</p>
              <p className="text-gray-500">Ext.</p>
            </div>
          </div>
        </div>
      )}
    </form>
  )
}
