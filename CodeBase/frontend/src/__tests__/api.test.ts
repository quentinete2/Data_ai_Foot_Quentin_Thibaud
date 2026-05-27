import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { predire, getStats } from '../api'

describe('predire()', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('fait un POST vers /api/predict avec le bon corps', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          prediction: 'Victoire France',
          confidence: 0.6,
          probabilities: { home_win: 0.6, draw: 0.25, away_win: 0.15 },
          home_stats: { avg_goals: 2.1, total_matches: 80, wins: 55 },
          away_stats: { avg_goals: 2.0, total_matches: 90, wins: 50 },
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      )
    )

    await predire({ home_team: 'France', away_team: 'Brazil' })

    expect(vi.mocked(fetch)).toHaveBeenCalledWith(
      'http://localhost:8000/api/predict',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ home_team: 'France', away_team: 'Brazil' }),
      })
    )
  })

  it('retourne les données parsées', async () => {
    const expected = {
      prediction: 'Victoire France',
      confidence: 0.6,
      probabilities: { home_win: 0.6, draw: 0.25, away_win: 0.15 },
      home_stats: { avg_goals: 2.1, total_matches: 80, wins: 55 },
      away_stats: { avg_goals: 2.0, total_matches: 90, wins: 50 },
    }
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify(expected), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    )
    const result = await predire({ home_team: 'France', away_team: 'Brazil' })
    expect(result).toEqual(expected)
  })

  it('lève une erreur sur réponse 422', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response('{"detail":"validation error"}', { status: 422 })
    )
    await expect(predire({ home_team: '', away_team: 'Brazil' })).rejects.toThrow('predict error 422')
  })

  it('lève une erreur sur réponse 503', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response('{"detail":"model manquant"}', { status: 503 })
    )
    await expect(predire({ home_team: 'France', away_team: 'Brazil' })).rejects.toThrow('predict error 503')
  })

  it('lève une erreur sur réponse 500', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response('{"detail":"erreur interne"}', { status: 500 })
    )
    await expect(predire({ home_team: 'France', away_team: 'Brazil' })).rejects.toThrow('predict error 500')
  })
})

describe('getStats()', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('fait un GET vers /api/stats', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({ top_teams_wins: [], top_teams_goals: [], metrics: { accuracy: 0.648 } }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      )
    )
    await getStats()
    expect(vi.mocked(fetch)).toHaveBeenCalledWith('http://localhost:8000/api/stats')
  })

  it('retourne la structure correcte', async () => {
    const expected = {
      top_teams_wins: [{ label: 'France', value: 72.5 }],
      top_teams_goals: [{ label: 'Brazil', value: 2.3 }],
      metrics: { accuracy: 0.648 },
    }
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify(expected), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    )
    const result = await getStats()
    expect(result).toEqual(expected)
  })

  it('lève une erreur sur réponse non-ok', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response('error', { status: 500 }))
    await expect(getStats()).rejects.toThrow('stats error 500')
  })
})
