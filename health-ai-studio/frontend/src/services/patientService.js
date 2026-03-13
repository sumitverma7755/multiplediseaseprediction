import apiClient from './apiClient';

export async function fetchPatients(params = {}) {
  const { data } = await apiClient.get('/patients', { params });
  return data;
}

export async function createPatient(payload) {
  const { data } = await apiClient.post('/patients', payload);
  return data;
}

export async function fetchPatientReports(patientId) {
  const { data } = await apiClient.get(`/patients/${patientId}/reports`);
  return data;
}
