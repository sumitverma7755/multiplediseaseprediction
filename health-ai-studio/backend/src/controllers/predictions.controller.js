import { predictWithModel } from '../services/mlClient.service.js';
import { findPatientById } from '../services/patientStore.service.js';
import { getPredictions, savePrediction, weeklyTrend } from '../services/predictionStore.service.js';

export async function createPrediction(req, res, next) {
  try {
    const { diseaseType, inputData, patientId } = req.body;

    if (!diseaseType || typeof inputData !== 'object') {
      const err = new Error('diseaseType and inputData are required');
      err.statusCode = 400;
      throw err;
    }

    let patientName = 'N/A';
    if (patientId) {
      const patient = await findPatientById(patientId);
      patientName = patient?.fullName || 'N/A';
    }

    const inference = await predictWithModel({ diseaseType, inputData, patientId });
    const prediction = await savePrediction({
      patientId: patientId || null,
      patientName,
      diseaseType,
      inputData,
      ...inference
    });

    res.status(201).json({ prediction });
  } catch (error) {
    next(error);
  }
}

export async function weeklyPredictionTrend(req, res, next) {
  try {
    const predictions = await getPredictions({ patientId: req.query.patientId || '' });
    const items = weeklyTrend(predictions);
    res.json({ items });
  } catch (error) {
    next(error);
  }
}
