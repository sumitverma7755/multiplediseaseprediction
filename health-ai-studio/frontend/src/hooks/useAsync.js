import { useCallback, useState } from 'react';

export function useAsync(asyncFn) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const execute = useCallback(
    async (...args) => {
      setLoading(true);
      setError('');
      try {
        const result = await asyncFn(...args);
        setData(result);
        return result;
      } catch (err) {
        setError(err.message || 'Operation failed');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [asyncFn]
  );

  return { data, loading, error, execute, setData, setError };
}
