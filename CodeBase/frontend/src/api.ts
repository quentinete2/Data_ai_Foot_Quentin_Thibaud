// URL de base de l'API FastAPI (dev : port 8000)
const API = 'http://localhost:8000'

export type StatItem = { label: string; value: number }

export async function getStats(): Promise<StatItem[]> {
  const r = await fetch(`${API}/api/stats`)
  if (!r.ok) throw new Error('Erreur API /stats')
  return r.json()
}

export async function predire(
  features: Record<string, unknown>,
): Promise<{ prediction: number | null }> {
  const r = await fetch(`${API}/api/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(features),
  })
  if (!r.ok) throw new Error('Erreur API /predict')
  return r.json()
}
