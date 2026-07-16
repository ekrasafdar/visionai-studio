"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.dashboard().then(setStats).catch((e) => setError(e.message));
    api.history(20).then(setHistory).catch(() => {});
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="font-display text-3xl font-bold mb-8">Dashboard</h1>

      {error && <p className="text-sm text-red-400 mb-4">{error} — log in to see your stats.</p>}

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          <Stat label="Total predictions" value={stats.total_predictions} />
          <Stat label="Avg confidence" value={`${Math.round(stats.avg_confidence * 100)}%`} />
          <Stat label="Avg inference time" value={`${Math.round(stats.avg_inference_time_ms)}ms`} />
          <Stat label="Active model" value={stats.active_model} />
        </div>
      )}

      {stats?.predictions_by_day?.length > 0 && (
        <div className="glass rounded-2xl p-6 mb-10 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats.predictions_by_day}>
              <XAxis dataKey="day" stroke="#94A3B8" fontSize={11} />
              <YAxis stroke="#94A3B8" fontSize={11} />
              <Tooltip contentStyle={{ background: "#0F172A", border: "1px solid rgba(255,255,255,.1)" }} />
              <Bar dataKey="count" fill="#3B82F6" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="glass rounded-2xl p-6">
        <h2 className="font-display text-lg mb-4">Prediction history</h2>
        {history.length === 0 ? (
          <p className="text-sm text-slate-500">No predictions yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-slate-500 uppercase">
                <th className="pb-2">Label</th><th className="pb-2">Confidence</th><th className="pb-2">Model</th><th className="pb-2">Time</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h) => (
                <tr key={h.id} className="border-t border-white/5">
                  <td className="py-2 capitalize">{h.predicted_label}</td>
                  <td className="py-2 font-mono">{(h.confidence * 100).toFixed(1)}%</td>
                  <td className="py-2">{h.model_name}</td>
                  <td className="py-2 font-mono text-slate-500">{Math.round(h.inference_time_ms)}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: any }) {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="font-mono text-2xl font-semibold">{value}</div>
      <div className="text-xs text-slate-500 mt-1">{label}</div>
    </div>
  );
}
