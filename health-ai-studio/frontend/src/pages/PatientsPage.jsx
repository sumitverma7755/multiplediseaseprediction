import { useMemo, useState } from 'react';
import { Plus } from 'lucide-react';
import PatientFormModal from '../components/patients/PatientFormModal';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorState from '../components/ui/ErrorState';
import { usePatients } from '../hooks/usePatients';
import { fetchPatientReports } from '../services/patientService';
import { formatDateTime } from '../utils/date';

export default function PatientsPage() {
  const { patients, loading, error, addPatient, loadPatients } = usePatients();
  const [open, setOpen] = useState(false);
  const [reportsByPatient, setReportsByPatient] = useState({});

  const patientCountLabel = useMemo(() => `${patients.length} patient profiles`, [patients]);

  const loadReports = async (patientId) => {
    const response = await fetchPatientReports(patientId);
    setReportsByPatient((current) => ({ ...current, [patientId]: response.items || [] }));
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-panel">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Patients</h1>
            <p className="text-sm text-slate-600">Manage patient profiles, store screening results per patient, and access previous reports.</p>
            <p className="mt-1 text-xs text-slate-500">{patientCountLabel}</p>
          </div>
          <button
            onClick={() => setOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-800"
          >
            <Plus className="h-4 w-4" />
            Add Patient
          </button>
        </div>
      </section>

      {loading ? <LoadingSpinner text="Loading patients..." /> : null}
      {error ? <ErrorState message={error} onRetry={loadPatients} /> : null}

      <section className="space-y-4">
        {patients.map((patient) => (
          <article key={patient.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">{patient.fullName}</h3>
                <p className="text-sm text-slate-600">
                  {patient.gender}, {patient.age} years • {patient.contact || 'No contact'}
                </p>
                <p className="mt-1 text-xs text-slate-500">Added: {formatDateTime(patient.createdAt)}</p>
              </div>
              <button
                onClick={() => loadReports(patient.id)}
                className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
              >
                View Previous Reports
              </button>
            </div>

            {reportsByPatient[patient.id] ? (
              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-100 text-slate-700">
                    <tr>
                      <th className="px-3 py-2">Date</th>
                      <th className="px-3 py-2">Disease</th>
                      <th className="px-3 py-2">Risk</th>
                      <th className="px-3 py-2">Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reportsByPatient[patient.id].map((report) => (
                      <tr key={report.id} className="border-t border-slate-100">
                        <td className="px-3 py-2">{formatDateTime(report.createdAt)}</td>
                        <td className="px-3 py-2">{report.diseaseType}</td>
                        <td className="px-3 py-2">{report.riskPercentage.toFixed(1)}%</td>
                        <td className="px-3 py-2">{report.confidenceScore.toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </article>
        ))}
      </section>

      <PatientFormModal open={open} onClose={() => setOpen(false)} onSubmit={addPatient} loading={loading} />
    </div>
  );
}
