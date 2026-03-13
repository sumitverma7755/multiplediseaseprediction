export async function getAssistantReply({ question, context }) {
  const normalized = (question || '').toLowerCase();

  if (normalized.includes('confidence')) {
    return {
      answer: 'Confidence indicates how certain the model is with the current inputs. Higher confidence still requires clinical validation before treatment decisions.'
    };
  }

  if (normalized.includes('risk') || normalized.includes('high')) {
    return {
      answer: 'Risk category is generated from risk percentage bands: Low (<35), Moderate (35-69), High (>=70). Use it to prioritize follow-up, not as a final diagnosis.'
    };
  }

  if (normalized.includes('diet') || normalized.includes('lifestyle')) {
    return {
      answer: 'Lifestyle recommendations: keep a balanced diet, maintain moderate exercise 150 minutes/week, track sleep, reduce tobacco/alcohol exposure, and monitor vital markers regularly.'
    };
  }

  return {
    answer: `Health AI response (${context || 'general'}): I can explain prediction outputs, risk categories, and next-step preventive actions. Please share the specific result you want to understand.`
  };
}
