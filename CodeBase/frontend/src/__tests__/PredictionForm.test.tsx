import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import PredictionForm from '../PredictionForm'

vi.mock('../api', () => ({
  predire: vi.fn(),
}))

import { predire } from '../api'
const mockPredire = vi.mocked(predire)

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({
    defaultOptions: { mutations: { retry: false } },
  })
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>)
}

const MOCK_RESULT = {
  prediction: 'Victoire France',
  confidence: 0.6,
  probabilities: { home_win: 0.6, draw: 0.25, away_win: 0.15 },
  home_stats: { avg_goals: 2.1, total_matches: 80, wins: 55 },
  away_stats: { avg_goals: 2.0, total_matches: 90, wins: 50 },
}

describe('PredictionForm — rendu initial', () => {
  it('affiche le label Équipe à domicile', () => {
    renderWithQuery(<PredictionForm />)
    expect(screen.getByLabelText(/domicile/i)).toBeInTheDocument()
  })

  it("affiche le label Équipe à l'extérieur", () => {
    renderWithQuery(<PredictionForm />)
    expect(screen.getByLabelText(/extérieur/i)).toBeInTheDocument()
  })

  it('pré-remplit France / Brazil', () => {
    renderWithQuery(<PredictionForm />)
    expect(screen.getByLabelText(/domicile/i)).toHaveValue('France')
    expect(screen.getByLabelText(/extérieur/i)).toHaveValue('Brazil')
  })

  it('le bouton Prédire est activé initialement', () => {
    renderWithQuery(<PredictionForm />)
    expect(screen.getByRole('button', { name: /prédire/i })).not.toBeDisabled()
  })
})

describe('PredictionForm — validation côté client', () => {
  beforeEach(() => {
    mockPredire.mockReset()
  })

  it('affiche une erreur et ne soumet pas si home_team est vide', async () => {
    const user = userEvent.setup()
    renderWithQuery(<PredictionForm />)
    await user.clear(screen.getByLabelText(/domicile/i))
    await user.click(screen.getByRole('button', { name: /prédire/i }))
    expect(await screen.findByText(/domicile.*requis/i)).toBeInTheDocument()
    expect(mockPredire).not.toHaveBeenCalled()
  })

  it("affiche une erreur et ne soumet pas si away_team est vide", async () => {
    const user = userEvent.setup()
    renderWithQuery(<PredictionForm />)
    await user.clear(screen.getByLabelText(/extérieur/i))
    await user.click(screen.getByRole('button', { name: /prédire/i }))
    expect(await screen.findByText(/extérieur.*requis/i)).toBeInTheDocument()
    expect(mockPredire).not.toHaveBeenCalled()
  })

  it('ne soumet pas si home_team contient uniquement des espaces', async () => {
    const user = userEvent.setup()
    renderWithQuery(<PredictionForm />)
    await user.clear(screen.getByLabelText(/domicile/i))
    await user.type(screen.getByLabelText(/domicile/i), '   ')
    await user.click(screen.getByRole('button', { name: /prédire/i }))
    expect(mockPredire).not.toHaveBeenCalled()
  })

  it("appelle predire avec le nom trimmé", async () => {
    const user = userEvent.setup()
    mockPredire.mockResolvedValueOnce(MOCK_RESULT)
    renderWithQuery(<PredictionForm />)
    await user.clear(screen.getByLabelText(/domicile/i))
    await user.type(screen.getByLabelText(/domicile/i), '  France  ')
    await user.click(screen.getByRole('button', { name: /prédire/i }))
    // TanStack Query v5 appelle mutationFn(variables, context) — on vérifie le 1er arg
    await waitFor(() => {
      expect(mockPredire).toHaveBeenCalled()
      expect(mockPredire.mock.calls[0][0]).toMatchObject({ home_team: 'France' })
    })
  })

  it("l'erreur disparaît quand l'utilisateur retape dans le champ", async () => {
    const user = userEvent.setup()
    renderWithQuery(<PredictionForm />)
    await user.clear(screen.getByLabelText(/domicile/i))
    await user.click(screen.getByRole('button', { name: /prédire/i }))
    expect(await screen.findByText(/domicile.*requis/i)).toBeInTheDocument()
    await user.type(screen.getByLabelText(/domicile/i), 'A')
    expect(screen.queryByText(/domicile.*requis/i)).not.toBeInTheDocument()
  })
})

describe('PredictionForm — soumission et résultat', () => {
  beforeEach(() => {
    mockPredire.mockReset()
  })

  it('désactive le bouton pendant la mutation', async () => {
    const user = userEvent.setup()
    mockPredire.mockReturnValueOnce(new Promise(() => {}))
    renderWithQuery(<PredictionForm />)
    await user.click(screen.getByRole('button', { name: /prédire/i }))
    expect(await screen.findByRole('button', { name: /cours/i })).toBeDisabled()
  })

  it('affiche le résultat après une réponse réussie', async () => {
    const user = userEvent.setup()
    mockPredire.mockResolvedValueOnce(MOCK_RESULT)
    renderWithQuery(<PredictionForm />)
    await user.click(screen.getByRole('button', { name: /prédire/i }))
    expect(await screen.findByText('Victoire France')).toBeInTheDocument()
  })

  it("affiche un message d'erreur en cas d'échec API", async () => {
    const user = userEvent.setup()
    mockPredire.mockRejectedValueOnce(new Error('predict error 500'))
    renderWithQuery(<PredictionForm />)
    await user.click(screen.getByRole('button', { name: /prédire/i }))
    expect(await screen.findByText(/erreur/i)).toBeInTheDocument()
  })

  it('affiche les trois probabilités après une prédiction', async () => {
    const user = userEvent.setup()
    mockPredire.mockResolvedValueOnce({
      prediction: 'Match Nul',
      confidence: 0.5,
      probabilities: { home_win: 0.3, draw: 0.5, away_win: 0.2 },
      home_stats: { avg_goals: 1.5, total_matches: 30, wins: 10 },
      away_stats: { avg_goals: 1.6, total_matches: 30, wins: 11 },
    })
    renderWithQuery(<PredictionForm />)
    await user.click(screen.getByRole('button', { name: /prédire/i }))
    await screen.findByText('Match Nul')
    expect(screen.getByText('30.0 %')).toBeInTheDocument()
    expect(screen.getByText('50.0 %')).toBeInTheDocument()
    expect(screen.getByText('20.0 %')).toBeInTheDocument()
  })
})
