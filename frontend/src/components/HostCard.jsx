import { useState } from "react";

export default function HostCard({ host, selected, onSelect, onRemove, onManualPing }) {
  const [pinging, setPinging] = useState(false);

  const isUp = host.latest_status === "UP";
  const statusLabel = host.latest_status ?? "UNKNOWN";

  const handlePing = async (e) => {
    e.stopPropagation();
    setPinging(true);
    try {
      await onManualPing(host.id);
    } finally {
      setPinging(false);
    }
  };

  return (
    <div
      onClick={() => onSelect(host)}
      style={{
        ...styles.card,
        borderColor: isUp ? "#16a34a" : "#dc2626",
        boxShadow: selected ? "0 0 0 2px #2563eb" : "none",
      }}
    >
      <div style={styles.header}>
        <div>
          <span style={{ ...styles.dot, background: isUp ? "#16a34a" : "#dc2626" }} />
          <strong>{host.name}</strong>
          <span style={styles.ip}> ({host.ip_address})</span>
        </div>
        <span style={{ color: isUp ? "#16a34a" : "#dc2626", fontWeight: 600 }}>{statusLabel}</span>
      </div>

      <div style={styles.meta}>
        <span>応答時間: {host.latest_response_time_ms != null ? `${host.latest_response_time_ms} ms` : "—"}</span>
        <span>稼働率: {host.uptime_percentage != null ? `${host.uptime_percentage}%` : "—"}</span>
      </div>

      <div style={styles.actions}>
        <button onClick={handlePing} disabled={pinging}>
          {pinging ? "Ping実行中..." : "手動Ping"}
        </button>
        {!host.is_default && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onRemove(host.id);
            }}
            style={styles.removeBtn}
          >
            削除
          </button>
        )}
      </div>
    </div>
  );
}

const styles = {
  card: {
    border: "2px solid",
    borderRadius: 8,
    padding: 16,
    background: "#fff",
    cursor: "pointer",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  dot: {
    display: "inline-block",
    width: 10,
    height: 10,
    borderRadius: "50%",
    marginRight: 8,
  },
  ip: { color: "#666", fontSize: 13 },
  meta: {
    display: "flex",
    gap: 16,
    marginTop: 8,
    fontSize: 13,
    color: "#444",
  },
  actions: {
    display: "flex",
    gap: 8,
    marginTop: 12,
  },
  removeBtn: {
    marginLeft: "auto",
    color: "#dc2626",
  },
};
