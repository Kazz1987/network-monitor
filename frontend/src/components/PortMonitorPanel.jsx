import { useState } from "react";
import { getErrorMessage } from "../api/client";
import { usePorts } from "../hooks/usePorts";

function formatDate(dt) {
  if (!dt) return "—";
  return new Date(dt).toLocaleString("ja-JP", { timeZone: "Asia/Tokyo", hour12: false });
}

export default function PortMonitorPanel({ hostId }) {
  const { ports, loading, error, addPort, removePort } = usePorts(hostId);
  const [portInput, setPortInput] = useState("");
  const [descInput, setDescInput] = useState("");
  const [formError, setFormError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleAdd = async (e) => {
    e.preventDefault();
    setFormError(null);
    const port = parseInt(portInput, 10);
    if (!Number.isInteger(port) || port < 1 || port > 65535) {
      setFormError("ポート番号は1〜65535の整数を入力してください");
      return;
    }
    setSubmitting(true);
    try {
      await addPort({ port, description: descInput.trim() || null });
      setPortInput("");
      setDescInput("");
    } catch (err) {
      setFormError(getErrorMessage(err, "ポートの追加に失敗しました"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={styles.section}>
      <h4 style={styles.title}>ポート監視</h4>
      {loading && <p style={styles.muted}>読み込み中...</p>}
      {error && <p style={styles.errorText}>{error}</p>}
      {!loading && ports.length === 0 && !error && (
        <p style={styles.muted}>登録済みポートはありません</p>
      )}
      {ports.map((pm) => {
        const color =
          pm.last_status === true ? "#16a34a" : pm.last_status === false ? "#dc2626" : "#9ca3af";
        const label =
          pm.last_status === true ? "OPEN" : pm.last_status === false ? "CLOSED" : "未チェック";
        return (
          <div key={pm.id} style={styles.portRow}>
            <span style={{ ...styles.dot, background: color }} />
            <span style={styles.portNum}>{pm.port}</span>
            <span style={styles.desc}>{pm.description || ""}</span>
            <span style={{ ...styles.statusLabel, color }}>{label}</span>
            <span style={styles.checkedAt}>{formatDate(pm.last_checked_at)}</span>
            <button style={styles.deleteBtn} onClick={() => removePort(pm.id)}>
              削除
            </button>
          </div>
        );
      })}
      <form onSubmit={handleAdd} style={styles.form}>
        <input
          type="number"
          placeholder="ポート番号"
          value={portInput}
          onChange={(e) => setPortInput(e.target.value)}
          min={1}
          max={65535}
          style={styles.portInput}
        />
        <input
          type="text"
          placeholder="説明（任意）"
          value={descInput}
          onChange={(e) => setDescInput(e.target.value)}
          maxLength={200}
          style={styles.descInput}
        />
        <button type="submit" disabled={submitting}>
          {submitting ? "追加中..." : "追加"}
        </button>
      </form>
      {formError && <p style={styles.errorText}>{formError}</p>}
    </div>
  );
}

const styles = {
  section: {
    marginTop: 16,
    paddingTop: 16,
    borderTop: "1px solid #e5e7eb",
  },
  title: {
    margin: "0 0 8px",
    fontSize: 14,
    fontWeight: 600,
    color: "#374151",
  },
  muted: {
    fontSize: 13,
    color: "#6b7280",
    margin: "4px 0",
  },
  portRow: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: "4px 0",
    fontSize: 13,
    borderBottom: "1px solid #f3f4f6",
  },
  dot: {
    display: "inline-block",
    width: 8,
    height: 8,
    borderRadius: "50%",
    flexShrink: 0,
  },
  portNum: {
    fontWeight: 600,
    minWidth: 40,
    fontVariantNumeric: "tabular-nums",
  },
  desc: {
    color: "#6b7280",
    flex: 1,
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    fontSize: 12,
  },
  statusLabel: {
    fontSize: 11,
    fontWeight: 600,
    minWidth: 52,
    textAlign: "right",
  },
  checkedAt: {
    color: "#9ca3af",
    fontSize: 11,
    minWidth: 80,
    textAlign: "right",
  },
  deleteBtn: {
    fontSize: 12,
    color: "#dc2626",
    padding: "2px 6px",
    flexShrink: 0,
  },
  form: {
    display: "flex",
    gap: 6,
    marginTop: 10,
    flexWrap: "wrap",
  },
  portInput: {
    width: 90,
    padding: "6px 8px",
    border: "1px solid #ccc",
    borderRadius: 4,
    fontSize: 13,
  },
  descInput: {
    flex: 1,
    minWidth: 80,
    padding: "6px 8px",
    border: "1px solid #ccc",
    borderRadius: 4,
    fontSize: 13,
  },
  errorText: {
    color: "#dc2626",
    fontSize: 13,
    margin: "4px 0 0",
  },
};
