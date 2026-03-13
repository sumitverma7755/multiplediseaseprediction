import apiClient from './apiClient';

export async function runPrediction(payload) {
  const { data } = await apiClient.post('/predictions', payload);
  return data;
}

export async function getPredictionTrend(params = {}) {
  const { data } = await apiClient.get('/predictions/trends/weekly', { params });
  return data;
}
