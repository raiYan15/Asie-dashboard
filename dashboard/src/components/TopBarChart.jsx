import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, LabelList } from 'recharts'

export function TopBarChart({ title, data, xKey, yKey }) {
  if (!data) return null
  const rows = data.map((d, i) => ({ ...d, rank: i + 1, delta: d[`${xKey}_delta`] ?? d.delta }))
  return (
    <div className="card">
      <div className="card-head">
        <div>
          <p className="eyebrow">Comparative Intelligence</p>
          <h3>{title}</h3>
        </div>
      </div>
      <div style={{ width: '100%', height: 320 }}>
        <ResponsiveContainer>
          <BarChart data={rows} layout="vertical" margin={{ left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey={yKey} type="category" width={160} />
            <Tooltip formatter={(value, name, props) => {
              if (name === xKey) return [value, 'Score']
              return [value, name]
            }} labelFormatter={() => 'Ranked list'}
            contentStyle={{ fontSize: 12 }} />
            <Bar dataKey={xKey} fill="#1d4ed8" radius={[4, 4, 4, 4]}>
              <LabelList dataKey="rank" position="insideLeft" offset={-30} fill="#0f172a" fontSize={12} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
