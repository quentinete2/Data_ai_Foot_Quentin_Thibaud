import { useState, type FormEvent } from 'react'
import { useMutation } from '@tanstack/react-query'
import { predire } from './api'

export default function PredictionForm() {
  // TODO (Claude Code) : 1 champ par feature de VOTRE modele (cf. J2)
  const [valeurs, setValeurs] = useState<Record<string, unknown>>({})

  const mutation = useMutation({ mutationFn: predire })

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    mutation.mutate(valeurs)
  }

  return (
    <form onSubmit={onSubmit} className="space-y-3">
      {/* TODO : generer les <input> a partir des features, mettre a jour `valeurs` via setValeurs */}
      <button
        type="submit"
        className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
        disabled={mutation.isPending}
      >
        {mutation.isPending ? '…' : 'Prédire'}
      </button>
      {mutation.data?.prediction != null && (
        <p>Prédiction : <strong>{String(mutation.data.prediction)}</strong></p>
      )}
      {mutation.isError && <p className="text-red-600">{(mutation.error as Error).message}</p>}
    </form>
  )
}
