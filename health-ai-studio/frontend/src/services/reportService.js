import apiClient from './apiClient';

export async function downloadHealthReport(predictionId) {
  const response = await apiClient.get(`/reports/prediction/${predictionId}`, {
    responseType: 'blob'
  });
  return response.data;
}

export async function downloadHistoryExport(params = {}) {
  const response = await apiClient.get('/reports/history', {
    params,
    responseType: 'blob'
  });
  return response.data;
}
