import { useEffect, useState } from 'react';
import { createPatient, fetchPatients } from '../services/patientService';

export function usePatients() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadPatients = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetchPatients();
      setPatients(response.items || []);
    } catch (err) {
      setError(err.message || 'Unable to load patients');
    } finally {
      setLoading(false);
    }
  };

  const addPatient = async (payload) => {
    setLoading(true);
    setError('');
    try {
      await createPatient(payload);
      await loadPatients();
    } catch (err) {
      setError(err.message || 'Unable to create patient');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPatients();
  }, []);

  return { patients, loading, error, loadPatients, addPatient };
}
