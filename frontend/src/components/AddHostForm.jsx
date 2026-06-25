import { useState } from "react";
import { getErrorMessage } from "../api/client";
import { validateName, validateTarget } from "../utils/validators";

export default function AddHostForm({ onAdd }) {
  const [name, setName] = useState("");
  const [ipAddress, setIpAddress] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const nameResult = validateName(name);
    if (!nameResult.valid) {
      setError(nameResult.message);
      return;
    }
    const targetResult = validateTarget(ipAddress);
    if (!targetResult.valid) {
      setError(targetResult.message);
      return;
    }

    setSubmitting(true);
    try {
      await onAdd({ name: nameResult.value, ip_address: targetResult.value });
      setName("");
      setIpAddress("");
    } catch (err) {
      setError(getErrorMessage(err, "ホストの追加に失敗しました"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <input
        type="text"
        placeholder="ホスト名"
        value={name}
        onChange={(e) => setName(e.target.value)}
        maxLength={100}
        style={styles.input}
      />
      <input
        type="text"
        placeholder="IPアドレス または ホスト名 (プライベートIP不可)"
        value={ipAddress}
        onChange={(e) => setIpAddress(e.target.value)}
        maxLength={255}
        style={styles.input}
      />
      <button type="submit" disabled={submitting}>
        {submitting ? "追加中..." : "ホストを追加"}
      </button>
      {error && <p style={styles.error}>{error}</p>}
    </form>
  );
}

const styles = {
  form: {
    display: "flex",
    gap: 8,
    alignItems: "flex-start",
    flexWrap: "wrap",
    marginBottom: 16,
  },
  input: {
    padding: "8px 10px",
    border: "1px solid #ccc",
    borderRadius: 4,
    minWidth: 200,
  },
  error: {
    color: "#dc2626",
    width: "100%",
    margin: 0,
  },
};
