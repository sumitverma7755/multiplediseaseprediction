export function getRiskCategory(riskPercent) {
  if (riskPercent < 35) {
    return { label: 'Low', tone: 'text-emerald-600 bg-emerald-50 border-emerald-200' };
  }
  if (riskPercent < 70) {
    return { label: 'Moderate', tone: 'text-amber-600 bg-amber-50 border-amber-200' };
  }
  return { label: 'High', tone: 'text-rose-600 bg-rose-50 border-rose-200' };
}
