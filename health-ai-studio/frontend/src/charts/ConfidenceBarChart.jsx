import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export default function ConfidenceBarChart({ confidence }) {
  const data = [{ name: 'Confidence', score: confidence }];

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
      <h4 className="mb-3 text-sm font-semibold text-slate-800">Confidence Score</h4>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="name" tick={{ fill: '#475569', fontSize: 12 }} />
            <YAxis domain={[0, 100]} tick={{ fill: '#475569', fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="score" fill="#0369a1" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
