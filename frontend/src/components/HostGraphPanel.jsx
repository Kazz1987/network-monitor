import { useMetrics } from "../hooks/useMetrics";
import ResponseChart from "./ResponseChart";

export default function HostGraphPanel({ host, onClose }) {
  const { metrics, error } = useMetrics(host?.id ?? null);

  if (!host) return null;

  return (
    <div className="graph-panel" style={styles.panel}>
      <div style={styles.header}>
        <strong>{host.name} の応答時間</strong>
        <button onClick={onClose}>閉じる</button>
      </div>
      {error ? <p style={{ color: "#dc2626" }}>{error}</p> : <ResponseChart metrics={metrics} />}
    </div>
  );
}

const styles = {
  panel: {
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: 16,
    background: "#fff",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
};
