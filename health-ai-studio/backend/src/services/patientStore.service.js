import { v4 as uuidv4 } from 'uuid';
import { readCollection, writeCollection } from '../utils/dataStore.js';

const FILE_NAME = 'patients.json';

export async function getPatients({ search } = {}) {
  const patients = await readCollection(FILE_NAME);
  if (!search) {
    return patients;
  }
  const needle = search.toLowerCase();
  return patients.filter((patient) => patient.fullName.toLowerCase().includes(needle));
}

export async function createPatient(payload) {
  const patients = await readCollection(FILE_NAME);
  const next = {
    id: uuidv4(),
    fullName: payload.fullName,
    age: Number(payload.age),
    gender: payload.gender,
    contact: payload.contact || '',
    notes: payload.notes || '',
    createdAt: new Date().toISOString()
  };

  patients.unshift(next);
  await writeCollection(FILE_NAME, patients);
  return next;
}

export async function findPatientById(patientId) {
  const patients = await readCollection(FILE_NAME);
  return patients.find((patient) => patient.id === patientId) || null;
}
