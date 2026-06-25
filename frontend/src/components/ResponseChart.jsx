import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function ResponseChart({ metrics }) {
  const data = (metrics || []).map((m) => ({
    time: new Date(m.pinged_at).toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" }),
    responseTime: m.status === "UP" ? m.response_time_ms : null,
  }));

  if (data.length === 0) {
    return <p style={{ color: "#666" }}>過去24時間のデータがありません</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} unit="ms" />
        <Tooltip formatter={(value) => (value === null ? "DOWN" : `${value} ms`)} />
        <Line
          type="monotone"
          dataKey="responseTime"
          stroke="#2563eb"
          dot={false}
          connectNulls={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
