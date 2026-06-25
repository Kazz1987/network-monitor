import { useEffect, useState } from "react";
import { getErrorMessage, settingsApi } from "../api/client";
import { validateInterval } from "../utils/validators";

const MIN_INTERVAL = 10;
const MAX_INTERVAL = 3600;

export default function SettingsPanel() {
  const [interval, setIntervalValue] = useState(60);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    settingsApi.get().then((data) => setIntervalValue(data.interval_seconds)).catch(() => {});
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSaved(false);

    const result = validateInterval(interval, MIN_INTERVAL, MAX_INTERVAL);
    if (!result.valid) {
      setError(result.message);
      return;
    }

    setSaving(true);
    try {
      await settingsApi.update({ interval_seconds: result.value });
      setSaved(true);
    } catch (err) {
      setError(getErrorMessage(err, "設定の更新に失敗しました"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.panel}>
      <label>
        監視間隔（秒）:
        <input
          type="number"
          min={MIN_INTERVAL}
          max={MAX_INTERVAL}
          value={interval}
          onChange={(e) => setIntervalValue(Number(e.target.value))}
          style={styles.input}
        />
      </label>
      <button type="submit" disabled={saving}>
        {saving ? "保存中..." : "保存"}
      </button>
      {saved && <span style={{ color: "#16a34a" }}>保存しました</span>}
      {error && <span style={{ color: "#dc2626" }}>{error}</span>}
    </form>
  );
}

const styles = {
  panel: {
    display: "flex",
    gap: 12,
    alignItems: "center",
    marginBottom: 16,
    padding: 12,
    background: "#f9fafb",
    borderRadius: 6,
  },
  input: {
    marginLeft: 8,
    width: 100,
    padding: "4px 6px",
  },
};
