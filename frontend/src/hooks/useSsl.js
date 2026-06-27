import { useCallback, useEffect, useState } from "react";
import { sslApi } from "../api/client";

const POLL_INTERVAL_MS = 300000; // 5分（SSL は1日1回チェックのため頻繁に更新不要）

export function useSsl(hostId) {
  const [ssl, setSsl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  const fetchSsl = useCallback(async () => {
    if (!hostId) return;
    setNotFound(false);
    try {
      const data = await sslApi.get(hostId);
      setSsl(data);
    } catch (err) {
      setSsl(null);
      if (err?.response?.status === 404) {
        setNotFound(true);
      }
    } finally {
      setLoading(false);
    }
  }, [hostId]);

  useEffect(() => {
    fetchSsl();
    const interval = setInterval(fetchSsl, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchSsl]);

  return { ssl, loading, notFound, refresh: fetchSsl };
}
