import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Download } from 'lucide-react';
import { SCREENING_INPUTS } from '../utils/constants';
import { getRiskCategory } from '../utils/risk';
import { runPrediction } from '../services/predictionService';
import { downloadHealthReport } from '../services/reportService';
import { downloadBlob } from '../utils/file';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorState from '../components/ui/ErrorState';
import RiskGaugeChart from '../charts/RiskGaugeChart';
import ConfidenceBarChart from '../charts/ConfidenceBarChart';
import FeatureImportanceChart from '../charts/FeatureImportanceChart';
import { usePatients } from '../hooks/usePatients';

export default function PredictionPage() {
  const { disease } = useParams();
  const { patients, loading: patientsLoading } = usePatients();
  const fields = useMemo(() => SCREENING_INPUTS[disease] || [], [disease]);

  const [formValues, setFormValues] = useState({});
  const [patientId, setPatientId] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const nextState = fields.reduce((acc, field) => {
      acc[field.id] = field.defaultValue;
      return acc;
    }, {});
    setFormValues(nextState);
  }, [fields]);

  useEffect(() => {
    if (patients.length && !patientId) {
      setPatientId(String(patients[0].id));
    }
  }, [patients, patientId]);

  const onInputChange = (field, value) => {
    setFormValues((current) => ({ ...current, [field]: Number(value) }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await runPrediction({
        diseaseType: disease,
        patientId: patientId ? Number(patientId) : null,
        inputData: formValues
      });
      setResult(response);
    } catch (err) {
      setError(err.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const onDownloadReport = async () => {
    if (!result?.prediction?.id) {
      return;
    }
    const file = await downloadHealthReport(result.prediction.id);
    downloadBlob(file, `ai-health-report-${result.prediction.id}.pdf`);
  };

  const category = getRiskCategory(result?.prediction?.riskPercentage || 0);

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-panel">
        <h1 className="text-2xl font-bold text-slate-900">{disease?.toUpperCase()} Screening</h1>
        <p className="mt-1 text-sm text-slate-600">
          Fill required inputs and submit to view risk percentage, category, explainability insights, and recommendations.
        </p>
      </section>

      {error ? <ErrorState message={error} /> : null}

      <section className="grid gap-6 lg:grid-cols-[1.1fr_1fr]">
        <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
          <div>
            <label className="text-sm font-medium text-slate-700">Patient</label>
            <select
              value={patientId}
              onChange={(event) => setPatientId(event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
              disabled={patientsLoading || !patients.length}
            >
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.fullName}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {fields.map((field) => (
              <label key={field.id} className="text-sm text-slate-700">
                {field.label}
                <input
                  type={field.type}
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  value={formValues[field.id] ?? ''}
                  onChange={(event) => onInputChange(field.id, event.target.value)}
                  className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
                  required
                />
              </label>
            ))}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-800 disabled:opacity-70"
          >
            {loading ? 'Generating Prediction...' : 'Submit Prediction'}
          </button>

          {loading ? <LoadingSpinner text="Running model inference..." /> : null}
        </form>

        <section className="space-y-4">
          {result ? (
            <>
              <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
                <p className="text-xs uppercase tracking-wide text-slate-500">Risk Percentage</p>
                <p className="mt-1 text-3xl font-bold text-slate-900">{result.prediction.riskPercentage.toFixed(1)}%</p>
                <div className={`mt-3 inline-flex rounded-lg border px-3 py-1 text-sm font-medium ${category.tone}`}>
                  Risk Category: {result.prediction.riskCategory}
                </div>
              </article>

              <RiskGaugeChart value={result.prediction.riskPercentage} />
              <ConfidenceBarChart confidence={result.prediction.confidenceScore} />

              <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
                <h4 className="mb-2 text-sm font-semibold text-slate-800">AI Recommendations</h4>
                <ul className="space-y-2 text-sm text-slate-700">
                  {result.prediction.recommendations.map((line, index) => (
                    <li key={`${line}-${index}`} className="rounded-lg bg-slate-50 px-3 py-2">
                      {line}
                    </li>
                  ))}
                </ul>
              </article>

              <button
                onClick={onDownloadReport}
                className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
              >
                <Download className="h-4 w-4" />
                Download AI Health Report
              </button>
            </>
          ) : (
            <article className="rounded-xl border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-600">
              Submit screening inputs to view risk percentage, category, explainability, and recommendations.
            </article>
          )}
        </section>
      </section>

      {result ? (
        <section className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
          <FeatureImportanceChart data={result.prediction.featureImportance} />
          <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
            <h4 className="mb-2 text-sm font-semibold text-slate-800">Important Features</h4>
            <p className="mb-3 text-sm text-slate-600">The model weighted these features highest while computing risk.</p>
            <ul className="space-y-2 text-sm text-slate-700">
              {result.prediction.featureImportance.map((item) => (
                <li key={item.feature} className="rounded-lg bg-slate-50 px-3 py-2">
                  <span className="font-semibold">{item.feature}</span> contributes {(item.importance * 100).toFixed(1)}%
                </li>
              ))}
            </ul>
          </article>
        </section>
      ) : null}
    </div>
  );
}
