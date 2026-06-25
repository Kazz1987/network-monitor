import { useState } from "react";
import { useHosts } from "../hooks/useHosts";
import AddHostForm from "./AddHostForm";
import AlertBanner from "./AlertBanner";
import "./Dashboard.css";
import HostCard from "./HostCard";
import HostGraphPanel from "./HostGraphPanel";
import SettingsPanel from "./SettingsPanel";

export default function Dashboard() {
  const { hosts, loading, error, addHost, removeHost, manualPing } = useHosts();
  const [selectedHostId, setSelectedHostId] = useState(null);

  const downHosts = hosts.filter((h) => h.latest_status === "DOWN");
  const upCount = hosts.filter((h) => h.latest_status === "UP").length;
  const selectedHost = hosts.find((h) => h.id === selectedHostId) ?? null;

  const handleSelectHost = (host) => {
    setSelectedHostId((prev) => (prev === host.id ? null : host.id));
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>ネットワーク死活監視ダッシュボード</h1>
        <div className="summary-badges">
          <span className="badge badge-up">UP {upCount}</span>
          <span className="badge badge-down">DOWN {downHosts.length}</span>
        </div>
      </div>

      <AlertBanner downHosts={downHosts} />

      <div className="top-row">
        <SettingsPanel />
        <AddHostForm onAdd={addHost} />
      </div>

      {loading && <p>読み込み中...</p>}
      {error && <p style={{ color: "#dc2626" }}>{error}</p>}
      {!loading && hosts.length === 0 && <p>監視対象のホストがありません。追加してください。</p>}

      <div className="content-row">
        <div className="host-grid">
          {hosts.map((host) => (
            <HostCard
              key={host.id}
              host={host}
              selected={host.id === selectedHostId}
              onSelect={handleSelectHost}
              onRemove={removeHost}
              onManualPing={manualPing}
            />
          ))}
        </div>

        {selectedHost && (
          <HostGraphPanel host={selectedHost} onClose={() => setSelectedHostId(null)} />
        )}
      </div>
    </div>
  );
}
