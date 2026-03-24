import { useState, useEffect, useCallback } from 'react';
import { apiFetch, ApiError } from '../api/client';

interface UseApiOptions<T> {
  autoFetch?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: ApiError | Error) => void;
  dependencies?: any[];
  pollingIntervalMs?: number;
}

export function useApi<T>(path: string, options: UseApiOptions<T> = {}) {
  const {
    autoFetch = true,
    onSuccess,
    onError,
    dependencies = [],
    pollingIntervalMs,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(autoFetch);
  const [error, setError] = useState<ApiError | Error | null>(null);

  const fetchResource = useCallback(async (overridePath?: string, fetchOptions?: RequestInit) => {
    setLoading(true);
    setError(null);
    try {
      const responseData = await apiFetch<T>(overridePath || path, fetchOptions);
      setData(responseData);
      if (onSuccess) onSuccess(responseData);
      return responseData;
    } catch (err: any) {
      setError(err);
      if (onError) onError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [path, onSuccess, onError]); // excluded dependencies intentionally to avoid infinite loops, but depends on path

  useEffect(() => {
    if (autoFetch) {
      fetchResource();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  // Polling logic
  useEffect(() => {
    if (pollingIntervalMs && pollingIntervalMs > 0 && autoFetch) {
      const interval = setInterval(() => {
        // fetch but don't set loading=true so UI doesn't stutter seamlessly
        apiFetch<T>(path)
          .then(res => {
            setData(res);
            if (onSuccess) onSuccess(res);
          })
          .catch(err => {
            // we don't necessarily want to set global error state on polling fail,
            // but for now we do.
            setError(err);
          });
      }, pollingIntervalMs);
      return () => clearInterval(interval);
    }
  }, [path, autoFetch, pollingIntervalMs, onSuccess]);

  // Optimistic update helper
  const mutate = useCallback((newData: T | ((prev: T | null) => T)) => {
    setData(prev => typeof newData === 'function' ? (newData as any)(prev) : newData);
  }, []);

  return { data, loading, error, refetch: fetchResource, mutate };
}
