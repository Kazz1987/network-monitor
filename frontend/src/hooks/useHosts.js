import { useCallback, useEffect, useRef, useState } from "react";
import { getErrorMessage, hostsApi } from "../api/client";

const POLL_INTERVAL_MS = 30000;

export function useHosts() {
  const [hosts, setHosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const fetchHosts = useCallback(async () => {
    try {
      const data = await hostsApi.list();
      setHosts(data);
      setError(null);
    } catch (err) {
      setError(getErrorMessage(err, "ホスト情報の取得に失敗しました"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHosts();
    intervalRef.current = setInterval(fetchHosts, POLL_INTERVAL_MS);
    return () => clearInterval(intervalRef.current);
  }, [fetchHosts]);

  const addHost = useCallback(
    async (payload) => {
      const newHost = await hostsApi.create(payload);
      setHosts((prev) => [...prev, newHost]);
      return newHost;
    },
    []
  );

  const removeHost = useCallback(async (hostId) => {
    try {
      await hostsApi.remove(hostId);
      setHosts((prev) => prev.filter((h) => h.id !== hostId));
      setError(null);
    } catch (err) {
      setError(getErrorMessage(err, "ホストの削除に失敗しました"));
    }
  }, []);

  const manualPing = useCallback(async (hostId) => {
    try {
      await hostsApi.ping(hostId);
      await fetchHosts();
      setError(null);
    } catch (err) {
      setError(getErrorMessage(err, "Pingの実行に失敗しました"));
    }
  }, [fetchHosts]);

  return { hosts, loading, error, refresh: fetchHosts, addHost, removeHost, manualPing };
}
