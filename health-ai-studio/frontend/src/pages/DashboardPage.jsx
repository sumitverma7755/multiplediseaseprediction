import { useEffect, useMemo, useState } from 'react';
import { Plus } from 'lucide-react';
import { DISEASE_MODULES } from '../utils/constants';
import ModuleCard from '../components/layout/ModuleCard';
import WeeklyTrendChart from '../charts/WeeklyTrendChart';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorState from '../components/ui/ErrorState';
import { fetchHistorySummary } from '../services/historyService';
import { getPredictionTrend } from '../services/predictionService';

export default function DashboardPage() {
  const [summary, setSummary] = useState({ totalPredictions: 0, avgConfidence: 0, highRiskCount: 0 });
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const cards = useMemo(
    () => [
      { label: 'Total Predictions', value: summary.totalPredictions },
      { label: 'Average Confidence', value: `${summary.avgConfidence.toFixed(1)}%` },
      { label: 'High Risk Cases', value: summary.highRiskCount }
    ],
    [summary]
  );

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [summaryRes, trendRes] = await Promise.all([fetchHistorySummary(), getPredictionTrend()]);
      setSummary(summaryRes);
      setTrend(trendRes.items || []);
    } catch (err) {
      setError(err.message || 'Unable to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return <LoadingSpinner text="Loading workspace snapshot..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={load} />;
  }

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-panel">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Workspace Snapshot</h1>
            <p className="mt-1 text-sm text-slate-600">Production-grade AI healthcare dashboard with explainability and patient-centric tracking.</p>
          </div>
          <button className="inline-flex items-center gap-2 rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-800">
            <Plus className="h-4 w-4" />
            New Screening
          </button>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        {cards.map((card) => (
          <article key={card.label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
            <p className="text-xs uppercase tracking-wide text-slate-500">{card.label}</p>
            <p className="mt-2 text-2xl font-bold text-slate-900">{card.value}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        {DISEASE_MODULES.map((module) => (
          <ModuleCard key={module.key} module={module} />
        ))}
      </section>

      <WeeklyTrendChart data={trend} />
    </div>
  );
}
