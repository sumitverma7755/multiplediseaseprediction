import { useState } from 'react';

const initialState = {
  fullName: '',
  age: '',
  gender: 'Female',
  contact: '',
  notes: ''
};

export default function PatientFormModal({ open, onClose, onSubmit, loading }) {
  const [form, setForm] = useState(initialState);

  if (!open) {
    return null;
  }

  const handleChange = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    await onSubmit({
      ...form,
      age: Number(form.age)
    });
    setForm(initialState);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/45 p-4">
      <div className="w-full max-w-xl rounded-2xl bg-white p-6 shadow-panel">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-xl font-semibold text-slate-900">Add Patient Profile</h3>
          <button onClick={onClose} className="rounded-lg px-2 py-1 text-slate-500 hover:bg-slate-100">
            x
          </button>
        </div>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <label className="text-sm text-slate-700">
            Full Name
            <input
              required
              value={form.fullName}
              onChange={(event) => handleChange('fullName', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
            />
          </label>

          <label className="text-sm text-slate-700">
            Age
            <input
              required
              type="number"
              min={0}
              value={form.age}
              onChange={(event) => handleChange('age', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
            />
          </label>

          <label className="text-sm text-slate-700">
            Gender
            <select
              value={form.gender}
              onChange={(event) => handleChange('gender', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
            >
              <option>Female</option>
              <option>Male</option>
              <option>Other</option>
            </select>
          </label>

          <label className="text-sm text-slate-700">
            Contact
            <input
              value={form.contact}
              onChange={(event) => handleChange('contact', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
            />
          </label>

          <label className="text-sm text-slate-700 sm:col-span-2">
            Medical Notes
            <textarea
              value={form.notes}
              onChange={(event) => handleChange('notes', event.target.value)}
              rows={3}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
            />
          </label>

          <div className="sm:col-span-2 flex justify-end gap-3">
            <button type="button" onClick={onClose} className="rounded-lg border border-slate-200 px-4 py-2 text-sm">
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-800 disabled:opacity-70"
            >
              {loading ? 'Saving...' : 'Save Patient'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
