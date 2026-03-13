import { useEffect, useMemo, useState } from 'react';
import { Download } from 'lucide-react';
import { fetchHistory } from '../services/historyService';
import { fetchPatients } from '../services/patientService';
import { downloadHistoryExport } from '../services/reportService';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorState from '../components/ui/ErrorState';
import { formatDateTime } from '../utils/date';
import { downloadBlob } from '../utils/file';

export default function HistoryPage() {
  const [filters, setFilters] = useState({ diseaseType: '', patientId: '', dateFrom: '', dateTo: '' });
  const [history, setHistory] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const diseaseOptions = useMemo(() => ['diabetes', 'heart', 'parkinsons'], []);

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [historyResponse, patientResponse] = await Promise.all([
        fetchHistory(filters),
        fetchPatients()
      ]);
      setHistory(historyResponse.items || []);
      setPatients(patientResponse.items || []);
    } catch (err) {
      setError(err.message || 'Unable to load history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onFilterChange = (field, value) => {
    setFilters((current) => ({ ...current, [field]: value }));
  };

  const applyFilters = async (event) => {
    event.preventDefault();
    await load();
  };

  const exportFile = async (format) => {
    const blob = await downloadHistoryExport({ ...filters, format });
    downloadBlob(blob, `history-export.${format === 'csv' ? 'csv' : 'pdf'}`);
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-panel">
        <h1 className="text-2xl font-bold text-slate-900">Prediction History</h1>
        <p className="mt-1 text-sm text-slate-600">Filter by disease, date, and patient. Export results in CSV or PDF.</p>
      </section>

      <form onSubmit={applyFilters} className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-panel sm:grid-cols-2 lg:grid-cols-5">
        <label className="text-sm text-slate-700">
          Disease Type
          <select
            value={filters.diseaseType}
            onChange={(event) => onFilterChange('diseaseType', event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
          >
            <option value="">All</option>
            {diseaseOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-slate-700">
          Patient
          <select
            value={filters.patientId}
            onChange={(event) => onFilterChange('patientId', event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
          >
            <option value="">All</option>
            {patients.map((patient) => (
              <option key={patient.id} value={patient.id}>
                {patient.fullName}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-slate-700">
          Date From
          <input
            type="date"
            value={filters.dateFrom}
            onChange={(event) => onFilterChange('dateFrom', event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
          />
        </label>

        <label className="text-sm text-slate-700">
          Date To
          <input
            type="date"
            value={filters.dateTo}
            onChange={(event) => onFilterChange('dateTo', event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
          />
        </label>

        <div className="flex items-end">
          <button className="w-full rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-800">Apply Filters</button>
        </div>
      </form>

      <section className="flex flex-wrap gap-3">
        <button
          onClick={() => exportFile('csv')}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100"
        >
          <Download className="h-4 w-4" />
          Export CSV
        </button>
        <button
          onClick={() => exportFile('pdf')}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100"
        >
          <Download className="h-4 w-4" />
          Export PDF
        </button>
      </section>

      {loading ? <LoadingSpinner text="Loading prediction history..." /> : null}
      {error ? <ErrorState message={error} onRetry={load} /> : null}

      <section className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-panel">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-100 text-slate-700">
            <tr>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Patient</th>
              <th className="px-4 py-3">Disease</th>
              <th className="px-4 py-3">Risk %</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Confidence</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item) => (
              <tr key={item.id} className="border-t border-slate-100">
                <td className="px-4 py-3">{formatDateTime(item.createdAt)}</td>
                <td className="px-4 py-3">{item.patientName || 'N/A'}</td>
                <td className="px-4 py-3">{item.diseaseType}</td>
                <td className="px-4 py-3">{item.riskPercentage.toFixed(1)}%</td>
                <td className="px-4 py-3">{item.riskCategory}</td>
                <td className="px-4 py-3">{item.confidenceScore.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
