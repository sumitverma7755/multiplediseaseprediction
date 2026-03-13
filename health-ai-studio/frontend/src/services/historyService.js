import apiClient from './apiClient';

export async function fetchHistory(filters = {}) {
  const { data } = await apiClient.get('/history', { params: filters });
  return data;
}

export async function fetchHistorySummary() {
  const { data } = await apiClient.get('/history/summary');
  return data;
}
