import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export default function FeatureImportanceChart({ data }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
      <h4 className="mb-3 text-sm font-semibold text-slate-800">Feature Importance</h4>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 24 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis type="number" domain={[0, 1]} tick={{ fill: '#475569', fontSize: 12 }} />
            <YAxis dataKey="feature" type="category" tick={{ fill: '#475569', fontSize: 12 }} width={120} />
            <Tooltip />
            <Bar dataKey="importance" fill="#7c3aed" radius={[0, 8, 8, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
