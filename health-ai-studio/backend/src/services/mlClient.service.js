import axios from 'axios';

const client = axios.create({
  baseURL: process.env.ML_API_URL || 'http://localhost:8000',
  timeout: 15000
});

function fallbackPrediction({ diseaseType, inputData }) {
  const values = Object.values(inputData || {}).map(Number).filter((value) => Number.isFinite(value));
  const normalized = values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
  const riskPercentage = Math.max(8, Math.min(96, (normalized % 100) + (diseaseType.length * 2)));
  const confidenceScore = Math.max(55, Math.min(98, 100 - Math.abs(50 - riskPercentage) / 2));

  const riskCategory = riskPercentage < 35 ? 'Low' : riskPercentage < 70 ? 'Moderate' : 'High';
  const featureImportance = Object.keys(inputData || {}).slice(0, 5).map((feature, idx) => ({
    feature,
    importance: Number((1 / (idx + 2)).toFixed(3))
  }));

  return {
    riskPercentage,
    confidenceScore,
    riskCategory,
    featureImportance,
    explanation: 'Fallback inference used because ML API was unavailable. Values are illustrative.',
    recommendations: [
      'Schedule routine clinical follow-up for verification.',
      'Improve sleep quality, hydration, and physical activity consistency.',
      'Track relevant biomarkers and repeat screening in 4 to 8 weeks.'
    ]
  };
}

export async function predictWithModel(payload) {
  try {
    const response = await client.post(`/predict/${payload.diseaseType}`, payload);
    return response.data;
  } catch (error) {
    return fallbackPrediction(payload);
  }
}
