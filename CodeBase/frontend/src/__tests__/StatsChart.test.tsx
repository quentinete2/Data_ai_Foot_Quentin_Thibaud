import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatsChart from '../StatsChart'

// jsdom ne fournit pas ResizeObserver requis par Recharts
global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// ResponsiveContainer retourne 0x0 en jsdom : on injecte des dimensions explicites
vi.mock('recharts', async () => {
  const actual = await vi.importActual<typeof import('recharts')>('recharts')
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: React.ReactElement }) =>
      React.cloneElement(children, { width: 600, height: 300 }),
  }
})

describe('StatsChart — data vide', () => {
  it('affiche un message si data est un tableau vide', () => {
    render(<StatsChart data={[]} />)
    expect(screen.getByText(/aucune donnée/i)).toBeInTheDocument()
  })

  it("ne rend pas de SVG si data est vide", () => {
    const { container } = render(<StatsChart data={[]} />)
    expect(container.querySelector('svg')).not.toBeInTheDocument()
  })
})

describe('StatsChart — données valides', () => {
  const sampleData = [
    { label: 'France', value: 72.5 },
    { label: 'Brazil', value: 66.7 },
    { label: 'Germany', value: 60.0 },
  ]

  it('se rend sans erreur avec des données valides', () => {
    expect(() => render(<StatsChart data={sampleData} />)).not.toThrow()
  })

  it('rend un SVG quand des données sont présentes', () => {
    const { container } = render(<StatsChart data={sampleData} />)
    expect(container.querySelector('svg')).toBeInTheDocument()
  })
})
