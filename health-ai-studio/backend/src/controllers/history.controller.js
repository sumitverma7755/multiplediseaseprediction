import { getPredictions, summarizePredictions } from '../services/predictionStore.service.js';

export async function listHistory(req, res, next) {
  try {
    const items = await getPredictions({
      diseaseType: req.query.diseaseType || '',
      patientId: req.query.patientId || '',
      dateFrom: req.query.dateFrom || '',
      dateTo: req.query.dateTo || ''
    });
    res.json({ items });
  } catch (error) {
    next(error);
  }
}

export async function historySummary(_req, res, next) {
  try {
    const predictions = await getPredictions();
    res.json(summarizePredictions(predictions));
  } catch (error) {
    next(error);
  }
}
