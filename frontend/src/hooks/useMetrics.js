import { useCallback, useEffect, useState } from "react";
import { getErrorMessage, hostsApi } from "../api/client";

const POLL_INTERVAL_MS = 30000;

export function useMetrics(hostId) {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = useCallback(async () => {
    if (!hostId) return;
    try {
      const data = await hostsApi.metrics(hostId);
      setMetrics(data);
      setError(null);
    } catch (err) {
      setError(getErrorMessage(err, "メトリクスの取得に失敗しました"));
    } finally {
      setLoading(false);
    }
  }, [hostId]);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchMetrics]);

  return { metrics, loading, error, refresh: fetchMetrics };
}
