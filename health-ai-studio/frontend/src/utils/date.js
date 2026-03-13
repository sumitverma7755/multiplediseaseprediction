export function formatDateTime(value) {
  if (!value) {
    return 'N/A';
  }
  const dt = new Date(value);
  if (Number.isNaN(dt.getTime())) {
    return value;
  }
  return dt.toLocaleString();
}
