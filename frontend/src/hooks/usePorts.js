import { useCallback, useEffect, useState } from "react";
import { getErrorMessage, portsApi } from "../api/client";

const POLL_INTERVAL_MS = 30000;

export function usePorts(hostId) {
  const [ports, setPorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPorts = useCallback(async () => {
    if (!hostId) return;
    try {
      const data = await portsApi.list(hostId);
      setPorts(data);
      setError(null);
    } catch (err) {
      setError(getErrorMessage(err, "ポート情報の取得に失敗しました"));
    } finally {
      setLoading(false);
    }
  }, [hostId]);

  useEffect(() => {
    fetchPorts();
    const interval = setInterval(fetchPorts, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchPorts]);

  const addPort = useCallback(
    async (payload) => {
      const newPort = await portsApi.create(hostId, payload);
      setPorts((prev) => [...prev, newPort]);
      return newPort;
    },
    [hostId]
  );

  const removePort = useCallback(
    async (portId) => {
      await portsApi.remove(hostId, portId);
      setPorts((prev) => prev.filter((p) => p.id !== portId));
    },
    [hostId]
  );

  return { ports, loading, error, refresh: fetchPorts, addPort, removePort };
}
