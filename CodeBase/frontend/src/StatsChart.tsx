import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import type { StatItem } from './api'

type Props = { data: StatItem[] }

export default function StatsChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 4, right: 16, bottom: 40, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" angle={-35} textAnchor="end" tick={{ fontSize: 11 }} />
        <YAxis unit="%" domain={[0, 100]} />
        <Tooltip formatter={(v: number) => [`${v.toFixed(1)} %`, 'Victoires']} />
        <Bar dataKey="value" fill="#1d4ed8" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
