"use client";

import React, { useState, useEffect } from "react";
import {
  Database,
  Shield,
  RefreshCw,
  Trash2,
  CheckCircle2,
  Clock,
  Navigation,
  Layers,
  Cpu,
  LogOut,
  MapPin,
} from "lucide-react";

export interface OptimizationLogEntry {
  id: number;
  scenario_name: string;
  algorithm: string;
  traffic_mode: string;
  n_stops: number;
  total_distance_km: number;
  total_time_min: number;
  time_saved_min: number;
  crossover_iteration: number | null;
  runtime_ms: number;
  created_at: string;
}

interface AdminPortalViewProps {
  token: string | null;
  username: string;
  onLogout: () => void;
}

export default function AdminPortalView({
  token,
  username,
  onLogout,
}: AdminPortalViewProps) {
  const [logs, setLogs] = useState<OptimizationLogEntry[]>([]);
  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [isPurging, setIsPurging] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/admin/logs");
      if (res.ok) {
        const data = await res.json();
        setLogs(data);
      }
    } catch {
      // Offline fallback
    } finally {
      setLoading(false);
    }
  };

  const fetchSystemInfo = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/admin/system");
      if (res.ok) {
        const data = await res.json();
        setSystemInfo(data);
      }
    } catch {
      // Offline fallback
    }
  };

  useEffect(() => {
    fetchLogs();
    fetchSystemInfo();
  }, []);

  const handleClearLogs = async () => {
    if (!token) return;
    if (!confirm("Are you sure you want to purge all historical optimization audit logs?")) return;

    setIsPurging(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/admin/logs", {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (res.ok) {
        setLogs([]);
      }
    } catch {
      // Error handling
    } finally {
      setIsPurging(false);
    }
  };

  return (
    <div className="w-full h-full flex flex-col gap-4 overflow-y-auto p-4 bg-bg-base">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-bg-surface border border-border rounded-lg">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-full bg-signal-green/20 border border-signal-green flex items-center justify-center text-signal-green">
            <Shield size={18} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-text-primary">Admin Operations Console</h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-signal-green/20 text-signal-green uppercase font-mono">
                Authenticated
              </span>
            </div>
            <p className="text-xs text-text-secondary">
              Logged in as <strong className="text-text-primary font-mono">{username}</strong> &bull; Full Audit & Fleet Privileges
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="px-3 py-1.5 text-xs rounded border border-border bg-bg-base text-text-secondary hover:text-text-primary transition-colors flex items-center gap-1.5"
          >
            <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleClearLogs}
            disabled={isPurging || logs.length === 0}
            className="px-3 py-1.5 text-xs rounded border border-signal-red/30 bg-signal-red/10 text-signal-red hover:bg-signal-red/20 transition-colors flex items-center gap-1.5 disabled:opacity-40"
          >
            <Trash2 size={12} />
            <span>{isPurging ? "Purging..." : "Clear Logs"}</span>
          </button>
          <button
            onClick={onLogout}
            className="px-3 py-1.5 text-xs rounded border border-border bg-bg-base text-text-secondary hover:text-signal-red transition-colors flex items-center gap-1.5"
          >
            <LogOut size={12} />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      {/* Database & System Telemetry Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="p-3 bg-bg-surface border border-border rounded flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs text-text-secondary font-medium">
            <span className="flex items-center gap-1.5">
              <Database size={13} className="text-signal-green" />
              <span>Database Engine</span>
            </span>
            <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-mono bg-signal-green/20 text-signal-green font-bold">
              {systemInfo?.database?.engine === "postgresql" ? "PostgreSQL" : "SQLite Live"}
            </span>
          </div>
          <span className="font-mono text-xs font-semibold text-text-primary truncate">
            {systemInfo?.database?.url_masked || "localhost:5432/egreen_quanta"}
          </span>
          <span className="text-[10px] text-text-secondary">
            Automatic zero-crash connection pooling & session lifecycle
          </span>
        </div>

        <div className="p-3 bg-bg-surface border border-border rounded flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs text-text-secondary font-medium">
            <span className="flex items-center gap-1.5">
              <MapPin size={13} className="text-signal-amber" />
              <span>Network Scale</span>
            </span>
            <span className="font-mono text-xs font-bold text-signal-amber">70+ km</span>
          </div>
          <span className="text-xs font-semibold text-text-primary">
            {systemInfo?.landmarks_count || 36} Hubs &bull; {systemInfo?.road_segments_count || 57} Arteries
          </span>
          <span className="text-[10px] text-text-secondary">
            Greater Coimbatore District & Interstate Logistics
          </span>
        </div>

        <div className="p-3 bg-bg-surface border border-border rounded flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs text-text-secondary font-medium">
            <span className="flex items-center gap-1.5">
              <Cpu size={13} className="text-signal-green" />
              <span>Supported Solvers</span>
            </span>
            <span className="font-mono text-xs font-bold text-signal-green">7 Solvers</span>
          </div>
          <span className="text-xs font-semibold text-text-primary truncate">
            QPSO &bull; Classical PSO &bull; GA (OX/PMX)
          </span>
          <span className="text-[10px] text-text-secondary">
            Clarke-Wright &bull; Cheapest Insertion &bull; Nearest-Neighbor
          </span>
        </div>
      </div>

      {/* Historical Optimization Audit Table */}
      <div className="flex-1 bg-bg-surface border border-border rounded-lg flex flex-col overflow-hidden">
        <div className="px-4 py-3 border-b border-border flex items-center justify-between bg-bg-base">
          <div className="flex items-center gap-2">
            <Clock size={14} className="text-text-secondary" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-text-primary">
              Optimization Run Audit Logs
            </h4>
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-bg-surface border border-border text-text-secondary font-mono">
              {logs.length} Total Runs
            </span>
          </div>
        </div>

        <div className="flex-1 overflow-x-auto overflow-y-auto">
          {logs.length === 0 ? (
            <div className="h-48 flex flex-col items-center justify-center text-text-secondary text-xs gap-1">
              <span>No optimization logs recorded yet in database.</span>
              <span className="text-[11px] opacity-70">Execute routes on the dashboard to log telemetry automatically.</span>
            </div>
          ) : (
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border bg-bg-base text-[11px] uppercase font-mono text-text-secondary">
                  <th className="py-2.5 px-3">ID</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Scenario</th>
                  <th className="py-2.5 px-3">Algorithm</th>
                  <th className="py-2.5 px-3">Stops</th>
                  <th className="py-2.5 px-3">Transit Time</th>
                  <th className="py-2.5 px-3">Distance</th>
                  <th className="py-2.5 px-3">Savings</th>
                  <th className="py-2.5 px-3">Crossover</th>
                  <th className="py-2.5 px-3">Latency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50 font-mono text-[11px]">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-bg-base/70 transition-colors">
                    <td className="py-2 px-3 text-text-secondary font-semibold">#{log.id}</td>
                    <td className="py-2 px-3 text-text-secondary whitespace-nowrap">{log.created_at}</td>
                    <td className="py-2 px-3 font-sans font-medium text-text-primary">{log.scenario_name}</td>
                    <td className="py-2 px-3">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-signal-green/20 text-signal-green">
                        {log.algorithm}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-text-primary">{log.n_stops} stops</td>
                    <td className="py-2 px-3 font-semibold text-text-primary">{log.total_time_min.toFixed(1)}m</td>
                    <td className="py-2 px-3 text-text-secondary">{log.total_distance_km.toFixed(1)} km</td>
                    <td className="py-2 px-3 text-signal-green font-bold">
                      {log.time_saved_min > 0 ? `-${log.time_saved_min.toFixed(1)}m` : "Baseline"}
                    </td>
                    <td className="py-2 px-3 text-signal-amber font-medium">
                      {log.crossover_iteration !== null ? `Iter ${log.crossover_iteration}` : "None"}
                    </td>
                    <td className="py-2 px-3 text-text-secondary">{log.runtime_ms.toFixed(1)} ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
