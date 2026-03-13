import {
  PolarAngleAxis,
  RadialBar,
  RadialBarChart,
  ResponsiveContainer
} from 'recharts';

export default function RiskGaugeChart({ value }) {
  const data = [{ name: 'risk', value }];

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
      <h4 className="mb-3 text-sm font-semibold text-slate-800">Risk Gauge</h4>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="85%"
            innerRadius="70%"
            outerRadius="100%"
            barSize={18}
            data={data}
            startAngle={180}
            endAngle={0}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
            <RadialBar dataKey="value" cornerRadius={10} fill="#0f8f7d" />
          </RadialBarChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-2 text-center text-2xl font-bold text-slate-900">{value.toFixed(1)}%</p>
    </div>
  );
}
