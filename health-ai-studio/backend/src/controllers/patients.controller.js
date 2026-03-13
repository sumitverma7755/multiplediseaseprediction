import { createPatient, getPatients } from '../services/patientStore.service.js';
import { getPredictionsByPatientId } from '../services/predictionStore.service.js';

export async function listPatients(req, res, next) {
  try {
    const items = await getPatients({ search: req.query.search || '' });
    res.json({ items });
  } catch (error) {
    next(error);
  }
}

export async function addPatient(req, res, next) {
  try {
    const { fullName, age, gender, contact, notes } = req.body;
    if (!fullName || !Number.isFinite(Number(age))) {
      const err = new Error('fullName and age are required');
      err.statusCode = 400;
      throw err;
    }

    const patient = await createPatient({ fullName, age, gender, contact, notes });
    res.status(201).json({ patient });
  } catch (error) {
    next(error);
  }
}

export async function listPatientReports(req, res, next) {
  try {
    const items = await getPredictionsByPatientId(req.params.patientId);
    res.json({ items });
  } catch (error) {
    next(error);
  }
}
