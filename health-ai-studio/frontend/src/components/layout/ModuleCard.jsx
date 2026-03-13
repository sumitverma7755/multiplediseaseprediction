import { Activity, HeartPulse, Brain, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const ICON_BY_KEY = {
  diabetes: Activity,
  heart: HeartPulse,
  parkinsons: Brain
};

export default function ModuleCard({ module }) {
  const Icon = ICON_BY_KEY[module.key] || Activity;
  return (
    <article className="card-hover rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <div className={`mb-2 inline-flex rounded-full bg-gradient-to-r px-3 py-1 text-xs font-semibold text-white ${module.color}`}>
            {module.statLabel}
          </div>
          <h3 className="text-lg font-bold text-slate-900">{module.title}</h3>
        </div>
        <div className="rounded-xl bg-slate-100 p-2 text-slate-700">
          <Icon className="h-5 w-5" />
        </div>
      </div>

      <p className="mb-4 text-sm leading-6 text-slate-600">{module.description}</p>

      <Link
        to={`/screening/${module.key}`}
        className="inline-flex items-center gap-2 rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-800"
      >
        Start Screening
        <ArrowRight className="h-4 w-4" />
      </Link>
    </article>
  );
}
