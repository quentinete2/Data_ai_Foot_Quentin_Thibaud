const API = 'http://localhost:8000'

export type MatchInput = {
  home_team: string
  away_team: string
}

export type TeamStats = {
  avg_goals: number
  total_matches: number
  wins: number
}

export type PredictResponse = {
  prediction: string
  confidence: number
  probabilities: {
    home_win: number
    draw: number
    away_win: number
  }
  home_stats: TeamStats
  away_stats: TeamStats
}

export type StatItem = { label: string; value: number }

export type StatsResponse = {
  top_teams_wins: StatItem[]
  top_teams_goals: StatItem[]
  form_scores: StatItem[]
  metrics: { accuracy: number }
}

export async function predire(match: MatchInput): Promise<PredictResponse> {
  const r = await fetch(`${API}/api/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(match),
  })
  if (!r.ok) throw new Error(`predict error ${r.status}`)
  return r.json()
}

export async function getStats(): Promise<StatsResponse> {
  const r = await fetch(`${API}/api/stats`)
  if (!r.ok) throw new Error(`stats error ${r.status}`)
  return r.json()
}
