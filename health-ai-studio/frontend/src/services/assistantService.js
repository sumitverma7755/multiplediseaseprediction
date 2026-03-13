import apiClient from './apiClient';

export async function askAssistant(payload) {
  const { data } = await apiClient.post('/assistant/chat', payload);
  return data;
}
