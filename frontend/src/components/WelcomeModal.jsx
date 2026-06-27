import { useState } from "react";

const STORAGE_KEY = "network_monitor_welcome_seen";

export default function WelcomeModal() {
  const [visible, setVisible] = useState(() => {
    return localStorage.getItem(STORAGE_KEY) !== "1";
  });

  const handleClose = () => {
    localStorage.setItem(STORAGE_KEY, "1");
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div style={styles.overlay} onClick={handleClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button style={styles.closeBtn} onClick={handleClose} aria-label="閉じる">
          ✕
        </button>

        <h2 style={styles.title}>ネットワーク監視ダッシュボード</h2>
        <p style={styles.summary}>
          ネットワークエンジニアとWebエンジニアの両方の知識を活かした
          リアルタイム監視ツール
        </p>

        <div style={styles.divider} />

        <div style={styles.grid}>
          <section>
            <h3 style={styles.sectionTitle}>使用技術</h3>
            <dl style={styles.dl}>
              <dt style={styles.dt}>バックエンド</dt>
              <dd style={styles.dd}>Python / FastAPI / SQLite</dd>
              <dt style={styles.dt}>フロントエンド</dt>
              <dd style={styles.dd}>React / Vite</dd>
              <dt style={styles.dt}>監視機能</dt>
              <dd style={styles.dd}>ping監視 / ポート監視 / SSL証明書チェック</dd>
              <dt style={styles.dt}>通知</dt>
              <dd style={styles.dd}>Slack Webhook</dd>
              <dt style={styles.dt}>デプロイ</dt>
              <dd style={styles.dd}>Render</dd>
            </dl>
          </section>

          <section>
            <h3 style={styles.sectionTitle}>主な機能</h3>
            <ul style={styles.ul}>
              <li>死活監視（ICMP ping）</li>
              <li>ポート死活監視（TCP接続確認）</li>
              <li>SSL証明書の有効期限監視</li>
              <li>ダウン検知時のSlack自動通知</li>
            </ul>
          </section>
        </div>

        <div style={styles.divider} />

        <p style={styles.author}>
          <strong>作者：KAZUKI（フリーランスエンジニア）</strong>
          <br />
          <span style={styles.authorSub}>ネットワークエンジニア × Webアプリ開発の二刀流</span>
        </p>

        <button style={styles.startBtn} onClick={handleClose}>
          ダッシュボードを見る
        </button>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    padding: 16,
  },
  modal: {
    position: "relative",
    background: "#fff",
    borderRadius: 12,
    padding: "32px 28px 24px",
    maxWidth: 560,
    width: "100%",
    maxHeight: "90vh",
    overflowY: "auto",
    boxShadow: "0 20px 60px rgba(0,0,0,0.2)",
    fontFamily: "system-ui, sans-serif",
  },
  closeBtn: {
    position: "absolute",
    top: 14,
    right: 16,
    background: "none",
    border: "none",
    fontSize: 18,
    color: "#9ca3af",
    cursor: "pointer",
    lineHeight: 1,
    padding: 4,
  },
  title: {
    margin: "0 0 10px",
    fontSize: 20,
    fontWeight: 700,
    color: "#111827",
  },
  summary: {
    margin: 0,
    fontSize: 14,
    color: "#4b5563",
    lineHeight: 1.6,
  },
  divider: {
    margin: "20px 0",
    borderTop: "1px solid #e5e7eb",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 24,
  },
  sectionTitle: {
    margin: "0 0 10px",
    fontSize: 13,
    fontWeight: 600,
    color: "#374151",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  dl: {
    margin: 0,
    display: "grid",
    gridTemplateColumns: "auto 1fr",
    gap: "4px 10px",
    fontSize: 13,
  },
  dt: {
    color: "#6b7280",
    whiteSpace: "nowrap",
  },
  dd: {
    margin: 0,
    color: "#111827",
  },
  ul: {
    margin: 0,
    paddingLeft: 18,
    fontSize: 13,
    color: "#111827",
    lineHeight: 2,
  },
  author: {
    margin: 0,
    fontSize: 14,
    color: "#111827",
    textAlign: "center",
  },
  authorSub: {
    fontSize: 13,
    color: "#6b7280",
  },
  startBtn: {
    display: "block",
    width: "100%",
    marginTop: 20,
    padding: "10px 0",
    background: "#2563eb",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
  },
};
