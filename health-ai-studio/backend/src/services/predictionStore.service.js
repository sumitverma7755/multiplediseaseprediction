import { v4 as uuidv4 } from 'uuid';
import { readCollection, writeCollection } from '../utils/dataStore.js';

const FILE_NAME = 'predictions.json';

export async function savePrediction(payload) {
  const predictions = await readCollection(FILE_NAME);
  const next = {
    id: uuidv4(),
    patientId: payload.patientId || null,
    patientName: payload.patientName || 'N/A',
    diseaseType: payload.diseaseType,
    inputData: payload.inputData || {},
    riskPercentage: Number(payload.riskPercentage),
    confidenceScore: Number(payload.confidenceScore),
    riskCategory: payload.riskCategory,
    featureImportance: payload.featureImportance || [],
    recommendations: payload.recommendations || [],
    explanation: payload.explanation || '',
    createdAt: new Date().toISOString()
  };

  predictions.unshift(next);
  await writeCollection(FILE_NAME, predictions);
  return next;
}

export async function getPredictions(filters = {}) {
  const predictions = await readCollection(FILE_NAME);

  return predictions.filter((item) => {
    if (filters.diseaseType && item.diseaseType !== filters.diseaseType) {
      return false;
    }
    if (filters.patientId && item.patientId !== filters.patientId) {
      return false;
    }
    if (filters.dateFrom) {
      const from = new Date(filters.dateFrom);
      if (new Date(item.createdAt) < from) {
        return false;
      }
    }
    if (filters.dateTo) {
      const to = new Date(filters.dateTo);
      to.setHours(23, 59, 59, 999);
      if (new Date(item.createdAt) > to) {
        return false;
      }
    }
    return true;
  });
}

export async function getPredictionById(predictionId) {
  const predictions = await readCollection(FILE_NAME);
  return predictions.find((item) => item.id === predictionId) || null;
}

export async function getPredictionsByPatientId(patientId) {
  const predictions = await readCollection(FILE_NAME);
  return predictions.filter((item) => item.patientId === patientId);
}

export function summarizePredictions(predictions) {
  const totalPredictions = predictions.length;
  const avgConfidence = totalPredictions
    ? predictions.reduce((sum, item) => sum + Number(item.confidenceScore || 0), 0) / totalPredictions
    : 0;

  const highRiskCount = predictions.filter((item) => Number(item.riskPercentage) >= 70).length;
  return { totalPredictions, avgConfidence, highRiskCount };
}

export function weeklyTrend(predictions) {
  const today = new Date();
  const days = [...Array(7)].map((_, idx) => {
    const date = new Date(today);
    date.setDate(today.getDate() - (6 - idx));
    return {
      key: date.toISOString().slice(0, 10),
      day: date.toLocaleDateString('en-US', { weekday: 'short' }),
      total: 0
    };
  });

  const bucket = Object.fromEntries(days.map((day) => [day.key, day]));
  predictions.forEach((prediction) => {
    const key = new Date(prediction.createdAt).toISOString().slice(0, 10);
    if (bucket[key]) {
      bucket[key].total += 1;
    }
  });

  return days;
}
