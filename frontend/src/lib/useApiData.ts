import { useEffect, useRef, useState, useCallback } from "react";

interface ApiDataState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

/**
 * Shared data-fetching hook so every screen gets the same three states
 * (loading / error / loaded) instead of each page inventing its own
 * `.catch(() => {})` that silently swallows a failed request and leaves the
 * screen looking like an empty-but-successful state.
 */
export function useApiData<T>(fetcher: () => Promise<T>, deps: React.DependencyList): ApiDataState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const requestId = useRef(0);

  const load = useCallback(() => {
    const id = ++requestId.current;
    setLoading(true);
    setError(null);
    fetcher()
      .then((result) => {
        if (id !== requestId.current) return;
        setData(result);
        setLoading(false);
      })
      .catch((err) => {
        if (id !== requestId.current) return;
        setError(err?.message ? String(err.message) : String(err));
        setLoading(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { data, loading, error, reload: load };
}
