import { useSsl } from "../hooks/useSsl";

function getDaysColor(days) {
  if (days == null) return "#9ca3af";
  if (days <= 30) return "#dc2626";
  if (days <= 60) return "#d97706";
  return "#16a34a";
}

function formatDate(dt) {
  if (!dt) return "—";
  return new Date(dt).toLocaleString("ja-JP", { timeZone: "Asia/Tokyo", hour12: false });
}

export default function SslPanel({ hostId }) {
  const { ssl, loading, notFound } = useSsl(hostId);

  return (
    <div style={styles.section}>
      <h4 style={styles.title}>SSL証明書</h4>
      {loading && <p style={styles.muted}>読み込み中...</p>}
      {!loading && notFound && (
        <p style={styles.muted}>未チェック（毎日9時 UTC に実行 / IPアドレスのみのホストは対象外）</p>
      )}
      {!loading && ssl && (
        <dl style={styles.grid}>
          <dt style={styles.label}>残り日数</dt>
          <dd style={{ ...styles.value, color: getDaysColor(ssl.days_until_expiry), fontWeight: 600 }}>
            {ssl.days_until_expiry != null ? `${ssl.days_until_expiry}日` : "取得不可"}
          </dd>
          <dt style={styles.label}>有効期限</dt>
          <dd style={styles.value}>{formatDate(ssl.expires_at)}</dd>
          <dt style={styles.label}>最終チェック</dt>
          <dd style={styles.value}>{formatDate(ssl.last_checked_at)}</dd>
        </dl>
      )}
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
  grid: {
    display: "grid",
    gridTemplateColumns: "auto 1fr",
    gap: "5px 12px",
    fontSize: 13,
    margin: 0,
  },
  label: {
    color: "#6b7280",
    margin: 0,
  },
  value: {
    color: "#111827",
    margin: 0,
  },
};
