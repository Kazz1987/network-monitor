export default function AlertBanner({ downHosts }) {
  if (!downHosts || downHosts.length === 0) return null;

  return (
    <div role="alert" style={styles.banner}>
      <strong>⚠ DOWN検知:</strong>{" "}
      {downHosts.map((h) => h.name).join(", ")} が応答していません。
    </div>
  );
}

const styles = {
  banner: {
    background: "#fdecea",
    color: "#611a15",
    border: "1px solid #f5c6cb",
    borderRadius: 6,
    padding: "12px 16px",
    marginBottom: 16,
    fontWeight: 500,
  },
};
